"""Única porta de entrada para a IA: todo o sistema deve chamar `chamar_ia`.

Cada chamada gera uma linha de auditoria (RequisicaoIA), inclusive as bloqueadas ou com erro,
e respeita a cota mensal de tokens do usuário.
"""
import os
import time
from dataclasses import dataclass

from django.conf import settings
from django.db.models import Sum
from django.utils import timezone

from commex.services.global_settings import decrypt_token, encrypt_token

from .models import ConfiguracaoIA, CotaUsuario, RequisicaoIA, StatusRequisicao
from .services.provedores import ErroProvedor, enviar

LIMITE_REGISTRO = 4000  # caracteres de pergunta/resposta guardados na auditoria


class IAError(Exception):
    """Erro de IA com mensagem segura para exibir ao usuário."""


class IADesabilitada(IAError):
    pass


class CotaExcedida(IAError):
    pass


@dataclass
class RespostaIA:
    texto: str
    tokens_entrada: int
    tokens_saida: int

    @property
    def tokens_total(self):
        return self.tokens_entrada + self.tokens_saida


def obter_configuracao() -> ConfiguracaoIA:
    config = ConfiguracaoIA.objects.order_by('id').first()
    if config is None:
        config = ConfiguracaoIA.objects.create(cota_mensal_padrao=getattr(settings, 'IA_COTA_MENSAL_PADRAO', 50000))
    return config


def salvar_api_key(config: ConfiguracaoIA, chave_plana: str):
    config.api_key = encrypt_token(chave_plana.strip())


def obter_api_key(config: ConfiguracaoIA) -> str:
    return decrypt_token(config.api_key) or os.getenv('IA_API_KEY', '')


def inicio_do_mes():
    agora = timezone.localtime()
    return agora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def tokens_consumidos_no_mes(usuario) -> int:
    dados = RequisicaoIA.objects.filter(
        usuario=usuario, status=StatusRequisicao.SUCESSO, criado_em__gte=inicio_do_mes()
    ).aggregate(e=Sum('tokens_entrada'), s=Sum('tokens_saida'))
    return (dados['e'] or 0) + (dados['s'] or 0)


def cota_do_usuario(usuario, config=None):
    """Retorna (cota_mensal, permitido)."""
    config = config or obter_configuracao()
    cota = CotaUsuario.objects.filter(usuario=usuario).first()
    if cota:
        return cota.cota_mensal, cota.permitido
    return config.cota_mensal_padrao, True


def _registrar(usuario, origem, config, pergunta, status, resposta='', erro='', entrada=0, saida=0, inicio=None):
    duracao = int((time.monotonic() - inicio) * 1000) if inicio else 0
    return RequisicaoIA.objects.create(
        usuario=usuario if getattr(usuario, 'pk', None) else None,
        origem=origem,
        provedor=config.provedor,
        modelo=config.modelo,
        pergunta=pergunta[:LIMITE_REGISTRO],
        resposta=resposta[:LIMITE_REGISTRO],
        tokens_entrada=entrada,
        tokens_saida=saida,
        status=status,
        erro=erro[:1000],
        duracao_ms=duracao,
    )


def chamar_ia(usuario, mensagens, sistema='', origem='geral', max_tokens=None, ignorar_cota=False) -> RespostaIA:
    """Envia `mensagens` ([{'role': 'user'|'assistant', 'content': str}, ...]) à IA configurada.

    Levanta IAError (ou subclasses) com mensagem apropriada para o usuário.
    """
    config = obter_configuracao()
    pergunta = next((m['content'] for m in reversed(mensagens) if m['role'] == 'user'), '')

    if not config.ativo:
        _registrar(usuario, origem, config, pergunta, StatusRequisicao.BLOQUEADA, erro='IA desabilitada.')
        raise IADesabilitada('A IA está desabilitada no momento.')

    if not ignorar_cota:
        cota, permitido = cota_do_usuario(usuario, config)
        if not permitido:
            _registrar(usuario, origem, config, pergunta, StatusRequisicao.BLOQUEADA, erro='Usuário sem permissão de IA.')
            raise CotaExcedida('Seu usuário não tem permissão para usar a IA.')
        if tokens_consumidos_no_mes(usuario) >= cota:
            _registrar(usuario, origem, config, pergunta, StatusRequisicao.BLOQUEADA, erro='Cota mensal excedida.')
            raise CotaExcedida('Você atingiu a cota mensal de tokens da IA.')

    api_key = obter_api_key(config)
    if not api_key:
        _registrar(usuario, origem, config, pergunta, StatusRequisicao.ERRO, erro='Chave da API não configurada.')
        raise IAError('A chave da API da IA ainda não foi configurada.')

    inicio = time.monotonic()
    try:
        texto, entrada, saida = enviar(config, api_key, mensagens, sistema, max_tokens or config.max_tokens)
    except ErroProvedor as exc:
        _registrar(usuario, origem, config, pergunta, StatusRequisicao.ERRO, erro=str(exc), inicio=inicio)
        raise IAError('Não foi possível obter resposta da IA agora. Tente novamente.') from exc

    _registrar(usuario, origem, config, pergunta, StatusRequisicao.SUCESSO, resposta=texto, entrada=entrada, saida=saida, inicio=inicio)
    return RespostaIA(texto=texto, tokens_entrada=entrada, tokens_saida=saida)
