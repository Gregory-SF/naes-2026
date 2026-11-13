from django.conf import settings
from django.db import models


class PapelMensagem(models.TextChoices):
    USUARIO = 'user', 'Usuário'
    ASSISTENTE = 'assistant', 'Assistente'


class Mensagem(models.Model):
    """Histórico da conversa do assistente, separado por usuário."""

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mensagens_assistente')
    papel = models.CharField(max_length=10, choices=PapelMensagem.choices)
    conteudo = models.TextField()
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['criado_em', 'id']
        indexes = [models.Index(fields=['usuario', 'criado_em'])]

    def __str__(self):
        return f'{self.usuario} [{self.papel}] {self.conteudo[:40]}'
