from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User

# Create your models here.
 
class PapelScrum(models.TextChoices):
    SCRUM_MASTER = 'SCRUM_MASTER', 'Scrum Master'
    DESENVOLVEDOR = 'DESENVOLVEDOR', 'Desenvolvedor'
    PRODUCT_OWNER = 'PRODUCT_OWNER', 'Product Owner'


class StatusProjeto(models.TextChoices):
    ATIVO = 'ATIVO', 'Ativo'
    INATIVO = 'INATIVO', 'Inativo'


class TipoRepositorio(models.TextChoices):
    BACKEND = 'BACKEND', 'Backend'
    FRONTEND = 'FRONTEND', 'Frontend'
    FULLSTACK = 'FULLSTACK', 'Fullstack'


class Organizacao(models.Model):
    nome = models.CharField(max_length=120)
    link = models.URLField(verbose_name='link da organização', unique=True)
    ano_letivo = models.PositiveSmallIntegerField()
    link_github_projects = models.URLField(
        verbose_name='link do GitHub Projects',
        help_text='Link do kanban da organização/projeto no GitHub Projects.',
        blank=True,
        null=True,
    )
    atualizado_em = models.DateTimeField(auto_now=True)
    cadastrado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.nome} ({self.ano_letivo})'

    class Meta:
        ordering = ['-ano_letivo', 'nome']
        constraints = [
            models.UniqueConstraint(
                fields=['nome', 'ano_letivo'],
                name='organizacao_nome_ano_letivo_unico',
            )
        ]


class Aluno(models.Model):
    nome = models.CharField(max_length=120)
    ra = models.CharField(max_length=20, unique=True, verbose_name='RA')
    email = models.EmailField(unique=True)
    usuario = models.OneToOneField(
        User,
        on_delete=models.PROTECT,
        related_name='aluno',
        null=True,
        blank=True,
    )
    atualizado_em = models.DateTimeField(auto_now=True)
    cadastrado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.nome} ({self.ra})'

    class Meta:
        ordering = ['nome']


class Equipe(models.Model):
    nome = models.CharField(max_length=120)
    organizacao = models.ForeignKey(Organizacao, on_delete=models.PROTECT, related_name='equipes')
    alunos = models.ManyToManyField(Aluno, through='MembroEquipe', related_name='equipes')
    atualizado_em = models.DateTimeField(auto_now=True)
    cadastrado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.nome} - {self.organizacao.nome}'

    class Meta:
        ordering = ['nome']
        constraints = [
            models.UniqueConstraint(
                fields=['organizacao', 'nome'],
                name='equipe_organizacao_nome_unico',
            )
        ]


class MembroEquipe(models.Model):
    equipe = models.ForeignKey(Equipe, on_delete=models.PROTECT, related_name='membros')
    aluno = models.ForeignKey(Aluno, on_delete=models.PROTECT, related_name='participacoes')
    papel = models.CharField(max_length=20, choices=PapelScrum.choices)
    cadastrado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.aluno.nome} - {self.equipe.nome} ({self.get_papel_display()})'

    class Meta:
        ordering = ['equipe__nome', 'aluno__nome']
        constraints = [
            models.UniqueConstraint(
                fields=['equipe', 'aluno'],
                name='membro_equipe_aluno_unico',
            ),
            models.UniqueConstraint(
                fields=['equipe', 'papel'],
                condition=Q(papel=PapelScrum.SCRUM_MASTER),
                name='membro_equipe_unico_scrum_master',
            ),
            models.UniqueConstraint(
                fields=['equipe', 'papel'],
                condition=Q(papel=PapelScrum.PRODUCT_OWNER),
                name='membro_equipe_unico_product_owner',
            ),
        ]


class Projeto(models.Model):
    nome = models.CharField(max_length=120)
    status = models.CharField(max_length=8, choices=StatusProjeto.choices, default=StatusProjeto.ATIVO)
    ano = models.PositiveSmallIntegerField()
    organizacao = models.ForeignKey(
        Organizacao,
        on_delete=models.PROTECT,
        related_name='projetos',
        null=True,
        blank=True,
    )
    equipe = models.ForeignKey(
        Equipe,
        on_delete=models.PROTECT,
        related_name='projetos',
        null=True,
        blank=True,
    )
    atualizado_em = models.DateTimeField(auto_now=True)
    cadastrado_em = models.DateTimeField(auto_now_add=True)

    def clean(self):
        mensagens = []

        if self.equipe_id and self.organizacao_id and self.equipe.organizacao_id != self.organizacao_id:
            mensagens.append('A equipe deve pertencer à mesma organização do projeto.')

        if self.equipe_id and not self.organizacao_id:
            mensagens.append('Informe a organização quando uma equipe for selecionada.')

        if self.equipe_id:
            quantidade_scrum_master = self.equipe.membros.filter(papel=PapelScrum.SCRUM_MASTER).count()
            quantidade_product_owner = self.equipe.membros.filter(papel=PapelScrum.PRODUCT_OWNER).count()

            if quantidade_scrum_master != 1:
                mensagens.append('A equipe deve ter exatamente 1 Scrum Master.')
            if quantidade_product_owner != 1:
                mensagens.append('A equipe deve ter exatamente 1 Product Owner.')

        if mensagens:
            raise ValidationError({'equipe': ' '.join(mensagens)})

    def __str__(self):
        return f'{self.nome} ({self.ano})'

    class Meta:
        ordering = ['-ano', 'nome']
        constraints = [
            models.UniqueConstraint(
                fields=['organizacao', 'nome', 'ano'],
                name='projeto_organizacao_nome_ano_unico',
            )
        ]


class Repositorio(models.Model):
    nome = models.CharField(max_length=120)
    link = models.URLField(unique=True)
    linguagem_principal = models.CharField(max_length=60, blank=True)
    tipo = models.CharField(max_length=10, choices=TipoRepositorio.choices)
    organizacao = models.ForeignKey(
        Organizacao,
        on_delete=models.PROTECT,
        related_name='repositorios',
    )
    atualizado_em = models.DateTimeField(auto_now=True)
    cadastrado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome

    class Meta:
        ordering = ['nome']


class Analise(models.Model):
    repositorio = models.ForeignKey(Repositorio, on_delete=models.PROTECT, related_name='analises')
    projeto = models.ForeignKey(Projeto, on_delete=models.PROTECT, related_name='analises')
    branch = models.CharField(max_length=100, default='main')
    quantidade_commits = models.PositiveIntegerField(default=0)
    quantidade_participantes = models.PositiveIntegerField(default=0)
    quantidade_pull_requests = models.PositiveIntegerField(default=0)
    quantidade_issues_abertas = models.PositiveIntegerField(default=0)
    quantidade_issues_fechadas = models.PositiveIntegerField(default=0)
    data_ultimo_commit = models.DateTimeField(null=True, blank=True)
    taxa_merge_pull_requests = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Percentual de PRs mergeadas, de 0 a 100.',
    )
    observacoes = models.TextField(blank=True)
    analisado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.repositorio_id and self.projeto_id:
            if self.repositorio.organizacao_id != self.projeto.organizacao_id:
                raise ValidationError({'projeto': 'O projeto deve pertencer à mesma organização do repositório informado.'})

    def __str__(self):
        return f'Análise de {self.repositorio.nome} ({self.branch})'

    class Meta:
        ordering = ['-analisado_em']