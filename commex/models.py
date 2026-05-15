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


class DiaSemana(models.TextChoices):
    SEGUNDA = 'SEGUNDA', 'Segunda-feira'
    TERCA = 'TERCA', 'Terca-feira'
    QUARTA = 'QUARTA', 'Quarta-feira'
    QUINTA = 'QUINTA', 'Quinta-feira'
    SEXTA = 'SEXTA', 'Sexta-feira'

class Sprint(models.Model):
    nome = models.CharField(max_length=120)
    data_inicio = models.DateField()
    data_fim = models.DateField()

    def __str__(self):
        return f'{self.nome} ({self.data_inicio} - {self.data_fim})'

    class Meta:
        ordering = ['-data_inicio', 'nome']


class Organizacao(models.Model):
    nome = models.CharField(max_length=120)
    ativo = models.BooleanField(default=True)
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


class Projeto(models.Model):
    nome = models.CharField(max_length=120)
    status = models.CharField(max_length=8, choices=StatusProjeto.choices, default=StatusProjeto.ATIVO)
    ano = models.PositiveSmallIntegerField()
    dias_aula = models.JSONField(default=list, blank=True)
    repositorios = models.ManyToManyField('Repositorio', related_name='projetos', blank=True)
    sprints = models.ManyToManyField(Sprint, related_name='projetos', blank=True)

    def __str__(self):
        return f'{self.nome} ({self.ano})'

    @property
    def dias_aula_display(self):
        labels = dict(DiaSemana.choices)
        return ', '.join(labels.get(dia, dia) for dia in self.dias_aula)

    class Meta:
        ordering = ['-ano', 'nome']
        constraints = [
            models.UniqueConstraint(
                fields=['nome', 'ano'],
                name='projeto_nome_ano_unico',
            )
        ]


class Equipe(models.Model):
    nome = models.CharField(max_length=120)
    projeto = models.ForeignKey(Projeto, on_delete=models.PROTECT, related_name='equipes')
    alunos = models.ManyToManyField(Aluno, through='MembroEquipe', related_name='equipes')

    def __str__(self):
        return f'{self.nome} - {self.projeto.nome}'

    class Meta:
        ordering = ['nome']
        constraints = [
            models.UniqueConstraint(
                fields=['projeto', 'nome'],
                name='equipe_projeto_nome_unico',
            )
        ]


class MembroEquipe(models.Model):
    equipe = models.ForeignKey(Equipe, on_delete=models.PROTECT, related_name='membros')
    aluno = models.ForeignKey(Aluno, on_delete=models.PROTECT, related_name='participacoes')
    papel = models.CharField(max_length=20, choices=PapelScrum.choices)

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


class Repositorio(models.Model):
    nome = models.CharField(max_length=120, blank=True)
    link = models.URLField(unique=True)
    alias = models.CharField(max_length=60, blank=True, help_text='Nome curto para exibição, ex: backend, frontend, etc.')
    linguagem_principal = models.CharField(max_length=60, blank=True)
    tipo = models.CharField(max_length=10, choices=TipoRepositorio.choices, blank=True)

    def __str__(self):
        return self.alias or  self.nome

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
            if not self.projeto.repositorios.filter(pk=self.repositorio_id).exists():
                raise ValidationError({'repositorio': 'O repositorio deve estar associado ao projeto informado.'})

    def __str__(self):
        return f'Análise de {self.repositorio.nome} ({self.branch})'

    class Meta:
        ordering = ['-analisado_em']