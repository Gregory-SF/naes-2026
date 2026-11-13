from django.conf import settings
from django.db import models


class ProvedorIA(models.TextChoices):
    ANTHROPIC = 'anthropic', 'Anthropic (Claude)'
    OPENAI = 'openai', 'OpenAI ou compatível'


class ConfiguracaoIA(models.Model):
    """Configuração única (singleton) da IA, editável na tela de configuração."""

    provedor = models.CharField(max_length=20, choices=ProvedorIA.choices, default=ProvedorIA.ANTHROPIC)
    modelo = models.CharField(max_length=120, default='claude-haiku-5-5')
    base_url = models.URLField(
        'URL base da API', blank=True,
        help_text='Opcional. Deixe vazio para usar o endereço padrão do provedor.',
    )
    api_key = models.TextField('chave da API', blank=True, help_text='Guardada criptografada.')
    max_tokens = models.PositiveIntegerField('máximo de tokens por resposta', default=800)
    temperatura = models.FloatField(default=0.3)
    cota_mensal_padrao = models.PositiveIntegerField(
        'cota mensal padrão (tokens por usuário)', default=50000,
        help_text='Vale para quem não tem cota própria na tela "IA por usuário".',
    )
    ativo = models.BooleanField('IA habilitada', default=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'configuração da IA'
        verbose_name_plural = 'configurações da IA'

    def __str__(self):
        return f'{self.get_provedor_display()} / {self.modelo}'


class CotaUsuario(models.Model):
    """Cota mensal de tokens de um usuário (sobrescreve a cota padrão)."""

    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cota_ia')
    cota_mensal = models.PositiveIntegerField('cota mensal de tokens')
    permitido = models.BooleanField('pode usar a IA', default=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'cota de usuário'
        verbose_name_plural = 'cotas de usuários'

    def __str__(self):
        return f'{self.usuario} - {self.cota_mensal} tokens/mês'


class StatusRequisicao(models.TextChoices):
    SUCESSO = 'SUCESSO', 'Sucesso'
    ERRO = 'ERRO', 'Erro'
    BLOQUEADA = 'BLOQUEADA', 'Bloqueada'


class RequisicaoIA(models.Model):
    """Auditoria: uma linha para cada chamada feita a chamar_ia (inclusive as que falharam)."""

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='requisicoes_ia'
    )
    origem = models.CharField(max_length=40, default='geral')
    provedor = models.CharField(max_length=20, blank=True)
    modelo = models.CharField(max_length=120, blank=True)
    pergunta = models.TextField(blank=True)
    resposta = models.TextField(blank=True)
    tokens_entrada = models.PositiveIntegerField(default=0)
    tokens_saida = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=10, choices=StatusRequisicao.choices)
    erro = models.TextField(blank=True)
    duracao_ms = models.PositiveIntegerField(default=0)
    criado_em = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-criado_em']
        verbose_name = 'requisição de IA'
        verbose_name_plural = 'requisições de IA'

    @property
    def tokens_total(self):
        return self.tokens_entrada + self.tokens_saida

    def __str__(self):
        return f'{self.criado_em:%d/%m/%Y %H:%M} - {self.usuario} - {self.status}'
