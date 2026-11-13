from datetime import date

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.template import Context, Template
from django.test import RequestFactory, TestCase
from django.urls import reverse

from .models import Equipe, Projeto, Sprint


def criar_coordenador(username):
    usuario = User.objects.create_user(username, password='senha-forte-123')
    grupo, _ = Group.objects.get_or_create(name=settings.GRUPO_COORDENADORES)
    usuario.groups.add(grupo)
    return usuario


class IsolamentoPorUsuarioTests(TestCase):
    """Cada usuário só lista, vê, altera e exclui os próprios registros."""

    def setUp(self):
        self.ana = criar_coordenador('ana')
        self.beto = criar_coordenador('beto')
        self.projeto_ana = Projeto.objects.create(nome='Projeto da Ana', ano=2026, cadastrado_por=self.ana)
        self.projeto_beto = Projeto.objects.create(nome='Projeto do Beto', ano=2026, cadastrado_por=self.beto)
        self.equipe_beto = Equipe.objects.create(nome='Equipe B', projeto=self.projeto_beto, cadastrado_por=self.beto)
        self.sprint_beto = Sprint.objects.create(
            nome='Sprint B', data_inicio=date(2026, 1, 1), data_fim=date(2026, 1, 15), cadastrado_por=self.beto
        )
        self.client.force_login(self.ana)

    def test_lista_mostra_apenas_registros_proprios(self):
        resposta = self.client.get(reverse('projeto-list'))
        self.assertContains(resposta, 'Projeto da Ana')
        self.assertNotContains(resposta, 'Projeto do Beto')
        self.assertNotContains(self.client.get(reverse('equipe-list')), 'Equipe B')
        self.assertNotContains(self.client.get(reverse('sprint-list')), 'Sprint B')

    def test_registro_de_outro_usuario_retorna_404(self):
        for nome in ['projeto-detail', 'projeto-update', 'projeto-delete']:
            self.assertEqual(self.client.get(reverse(nome, args=[self.projeto_beto.pk])).status_code, 404, nome)
        for nome in ['equipe-detail', 'equipe-update', 'equipe-delete']:
            self.assertEqual(self.client.get(reverse(nome, args=[self.equipe_beto.pk])).status_code, 404, nome)
        for nome in ['sprint-detail', 'sprint-update']:
            self.assertEqual(self.client.get(reverse(nome, args=[self.sprint_beto.pk])).status_code, 404, nome)

    def test_nao_exclui_projeto_de_outro_usuario(self):
        self.client.post(reverse('projeto-delete', args=[self.projeto_beto.pk]))
        self.assertTrue(Projeto.objects.filter(pk=self.projeto_beto.pk).exists())

    def test_exclusao_do_proprio_projeto_exibe_mensagem(self):
        resposta = self.client.post(reverse('projeto-delete', args=[self.projeto_ana.pk]), follow=True)
        self.assertFalse(Projeto.objects.filter(pk=self.projeto_ana.pk).exists())
        self.assertContains(resposta, 'excluído com sucesso')

    def test_sprint_criada_pertence_ao_usuario_logado(self):
        resposta = self.client.post(reverse('sprint-create'), {
            'nome': 'Nova', 'data_inicio': '2026-02-01', 'data_fim': '2026-02-10', 'ativo': 'on',
        }, follow=True)
        sprint = Sprint.objects.get(nome='Nova')
        self.assertEqual(sprint.cadastrado_por, self.ana)
        self.assertContains(resposta, 'Sprint criada com sucesso')


class FiltrosEPaginacaoTests(TestCase):
    def setUp(self):
        self.usuario = criar_coordenador('ana')
        for i in range(25):
            Projeto.objects.create(nome=f'Alpha {i:02d}', ano=2026, cadastrado_por=self.usuario)
        Projeto.objects.create(nome='Beta', ano=2025, cadastrado_por=self.usuario)
        self.client.force_login(self.usuario)

    def test_filtro_por_nome(self):
        resposta = self.client.get(reverse('projeto-list'), {'nome': 'beta'})
        self.assertContains(resposta, 'Beta')
        self.assertNotContains(resposta, 'Alpha 00')

    def test_paginacao_preserva_filtros(self):
        resposta = self.client.get(reverse('projeto-list'), {'nome': 'Alpha'})
        self.assertContains(resposta, 'nome=Alpha')
        self.assertContains(resposta, 'page=2')

    def test_templatetag_url_params(self):
        request = RequestFactory().get('/x/', {'nome': 'a', 'page': '1', 'status': 'ATIVO'})
        modelo = Template("{% load paginacao_tags %}{% url_params page=3 %}")
        saida = modelo.render(Context({'request': request}))
        self.assertIn('page=3', saida)
        self.assertIn('nome=a', saida)
        self.assertIn('status=ATIVO', saida)
        self.assertEqual(saida.count('page='), 1)
        sem_page = Template("{% load paginacao_tags %}{% url_params page='' %}").render(Context({'request': request}))
        self.assertNotIn('page=', sem_page)


class QueriesOtimizadasTests(TestCase):
    """O número de queries não deve crescer com a quantidade de registros (sem N+1)."""

    def _contar(self, nome):
        from django.db import connection
        from django.test.utils import CaptureQueriesContext

        with CaptureQueriesContext(connection) as contexto:
            self.assertEqual(self.client.get(reverse(nome)).status_code, 200)
        return len(contexto)

    def _popular(self, usuario, inicio, fim):
        for i in range(inicio, fim):
            projeto = Projeto.objects.create(nome=f'P{i}', ano=2026, cadastrado_por=usuario)
            Equipe.objects.create(nome=f'E{i}', projeto=projeto, cadastrado_por=usuario)
            sprint = Sprint.objects.create(
                nome=f'S{i}', data_inicio=date(2026, 1, 1), data_fim=date(2026, 1, 2), cadastrado_por=usuario
            )
            sprint.projetos.add(projeto)

    def test_listas_nao_tem_n_mais_1(self):
        usuario = criar_coordenador('ana')
        self.client.force_login(usuario)
        self._popular(usuario, 0, 2)
        antes = {n: self._contar(n) for n in ['index', 'projeto-list', 'equipe-list', 'sprint-list']}
        self._popular(usuario, 2, 10)
        depois = {n: self._contar(n) for n in antes}
        self.assertEqual(antes, depois)
