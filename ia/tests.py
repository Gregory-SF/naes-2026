import json
from unittest import mock

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from assistente.models import Mensagem
from assistente.servico import JANELA_MENSAGENS

from .models import CotaUsuario, RequisicaoIA, StatusRequisicao
from .servico import CotaExcedida, IAError, chamar_ia, obter_configuracao, salvar_api_key, tokens_consumidos_no_mes

ENVIAR = 'ia.servico.enviar'


def configurar_chave():
    config = obter_configuracao()
    salvar_api_key(config, 'chave-de-teste')
    config.save()


class ChamarIATests(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user('ana', password='x')
        configurar_chave()

    @mock.patch(ENVIAR, return_value=('Olá!', 10, 5))
    def test_sucesso_gera_auditoria_e_consumo(self, _):
        resposta = chamar_ia(self.usuario, [{'role': 'user', 'content': 'oi'}], origem='teste')
        self.assertEqual(resposta.texto, 'Olá!')
        registro = RequisicaoIA.objects.get()
        self.assertEqual((registro.status, registro.tokens_entrada, registro.tokens_saida), (StatusRequisicao.SUCESSO, 10, 5))
        self.assertEqual(tokens_consumidos_no_mes(self.usuario), 15)

    @mock.patch(ENVIAR, return_value=('x', 10, 5))
    def test_bloqueia_quando_cota_excedida(self, enviar):
        CotaUsuario.objects.create(usuario=self.usuario, cota_mensal=15)
        chamar_ia(self.usuario, [{'role': 'user', 'content': 'a'}])
        with self.assertRaises(CotaExcedida):
            chamar_ia(self.usuario, [{'role': 'user', 'content': 'b'}])
        self.assertEqual(enviar.call_count, 1)
        self.assertEqual(RequisicaoIA.objects.filter(status=StatusRequisicao.BLOQUEADA).count(), 1)

    def test_sem_chave_registra_erro(self):
        config = obter_configuracao()
        config.api_key = ''
        config.save()
        with mock.patch.dict('os.environ', {'IA_API_KEY': ''}):
            with self.assertRaises(IAError):
                chamar_ia(self.usuario, [{'role': 'user', 'content': 'oi'}])
        self.assertEqual(RequisicaoIA.objects.get().status, StatusRequisicao.ERRO)

    def test_chave_e_guardada_criptografada(self):
        self.assertNotIn('chave-de-teste', obter_configuracao().api_key)


class TelasIATests(TestCase):
    def setUp(self):
        self.coord = User.objects.create_user('coord', password='x')
        self.coord.groups.add(Group.objects.get_or_create(name=settings.GRUPO_COORDENADORES)[0])
        self.comum = User.objects.create_user('comum', password='x')

    def test_telas_administrativas_exigem_coordenador(self):
        self.client.force_login(self.comum)
        for nome in ['ia:requisicoes', 'ia:configuracao', 'ia:usuarios']:
            self.assertNotEqual(self.client.get(reverse(nome)).status_code, 200, nome)
        self.assertEqual(self.client.get(reverse('ia:meu-consumo')).status_code, 200)

    def test_coordenador_acessa_todas_as_telas(self):
        self.client.force_login(self.coord)
        for nome in ['ia:requisicoes', 'ia:configuracao', 'ia:usuarios', 'ia:meu-consumo']:
            self.assertEqual(self.client.get(reverse(nome)).status_code, 200, nome)

    @mock.patch(ENVIAR, return_value=('OK', 3, 1))
    def test_testar_conexao(self, _):
        configurar_chave()
        self.client.force_login(self.coord)
        resposta = self.client.post(reverse('ia:testar-conexao'), follow=True)
        self.assertContains(resposta, 'Conexão OK')
        self.assertEqual(RequisicaoIA.objects.get().origem, 'teste')


class AssistenteTests(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user('ana', password='x')
        configurar_chave()
        self.client.force_login(self.usuario)

    def perguntar(self, texto):
        return self.client.post(
            reverse('assistente-perguntar'), data=json.dumps({'pergunta': texto}), content_type='application/json'
        )

    @mock.patch(ENVIAR, return_value=('**Resposta**', 5, 5))
    def test_pergunta_grava_historico_e_audita(self, _):
        resposta = self.perguntar('Como cadastro uma equipe?')
        self.assertEqual(resposta.json()['resposta'], '**Resposta**')
        self.assertEqual(Mensagem.objects.filter(usuario=self.usuario).count(), 2)
        self.assertEqual(RequisicaoIA.objects.get().origem, 'assistente')

    @mock.patch(ENVIAR, return_value=('ok', 1, 1))
    def test_apenas_janela_de_mensagens_vai_para_a_ia(self, enviar):
        for i in range(8):
            Mensagem.objects.create(usuario=self.usuario, papel='user' if i % 2 == 0 else 'assistant', conteudo=f'm{i}')
        self.perguntar('nova pergunta')
        enviado = enviar.call_args.args[2]
        self.assertLessEqual(len(enviado), JANELA_MENSAGENS)
        self.assertEqual(enviado[0]['role'], 'user')
        self.assertEqual(enviado[-1]['content'], 'nova pergunta')
        self.assertIn('Contexto do sistema', enviar.call_args.args[3])  # contexto_projeto.md no system

    @mock.patch(ENVIAR, return_value=('ok', 1, 1))
    def test_historico_e_por_usuario(self, enviar):
        outro = User.objects.create_user('beto', password='x')
        Mensagem.objects.create(usuario=outro, papel='user', conteudo='segredo do beto')
        self.perguntar('oi')
        self.assertNotIn('segredo do beto', json.dumps(enviar.call_args.args[2]))
        self.assertNotContains(self.client.get(reverse('assistente')), 'segredo do beto')

    def test_exige_csrf(self):
        from django.test import Client
        cliente = Client(enforce_csrf_checks=True)
        cliente.force_login(self.usuario)
        resposta = cliente.post(reverse('assistente-perguntar'), data='{"pergunta":"oi"}', content_type='application/json')
        self.assertEqual(resposta.status_code, 403)

    def test_rejeita_pergunta_vazia_ou_longa(self):
        self.assertEqual(self.perguntar('   ').status_code, 400)
        self.assertEqual(self.perguntar('a' * 1001).status_code, 400)

    def test_exige_login(self):
        self.client.logout()
        self.assertEqual(self.perguntar('oi').status_code, 302)
