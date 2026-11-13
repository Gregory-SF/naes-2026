"""Chamadas HTTP aos provedores de IA (só stdlib, sem dependências extras)."""
import json
import urllib.error
import urllib.request

from ia.models import ProvedorIA

TIMEOUT_SEGUNDOS = 40
URL_PADRAO = {
    ProvedorIA.ANTHROPIC: 'https://api.anthropic.com',
    ProvedorIA.OPENAI: 'https://api.openai.com/v1',
}


class ErroProvedor(Exception):
    """Falha ao falar com o provedor (rede, autenticação, resposta inválida)."""


def _post_json(url, headers, corpo):
    requisicao = urllib.request.Request(
        url,
        data=json.dumps(corpo).encode('utf-8'),
        headers={'Content-Type': 'application/json', **headers},
        method='POST',
    )
    try:
        with urllib.request.urlopen(requisicao, timeout=TIMEOUT_SEGUNDOS) as resposta:
            return json.loads(resposta.read().decode('utf-8'))
    except urllib.error.HTTPError as exc:
        detalhe = exc.read().decode('utf-8', errors='replace')[:300]
        raise ErroProvedor(f'O provedor respondeu HTTP {exc.code}: {detalhe}') from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise ErroProvedor(f'Falha de conexão com o provedor: {exc}') from exc
    except ValueError as exc:
        raise ErroProvedor('Resposta do provedor não é um JSON válido.') from exc


def enviar(config, api_key, mensagens, sistema, max_tokens):
    """Retorna (texto, tokens_entrada, tokens_saida)."""
    base = (config.base_url or URL_PADRAO[config.provedor]).rstrip('/')

    if config.provedor == ProvedorIA.ANTHROPIC:
        corpo = {
            'model': config.modelo,
            'max_tokens': max_tokens,
            'temperature': config.temperatura,
            'messages': mensagens,
        }
        if sistema:
            corpo['system'] = sistema
        dados = _post_json(
            f'{base}/v1/messages',
            {'x-api-key': api_key, 'anthropic-version': '2023-06-01'},
            corpo,
        )
        try:
            texto = ''.join(b.get('text', '') for b in dados['content'] if b.get('type') == 'text')
            uso = dados.get('usage', {})
            return texto, int(uso.get('input_tokens', 0)), int(uso.get('output_tokens', 0))
        except (KeyError, TypeError) as exc:
            raise ErroProvedor('Resposta inesperada do provedor.') from exc

    corpo = {
        'model': config.modelo,
        'max_tokens': max_tokens,
        'temperature': config.temperatura,
        'messages': ([{'role': 'system', 'content': sistema}] if sistema else []) + list(mensagens),
    }
    dados = _post_json(f'{base}/chat/completions', {'Authorization': f'Bearer {api_key}'}, corpo)
    try:
        texto = dados['choices'][0]['message']['content'] or ''
        uso = dados.get('usage', {})
        return texto, int(uso.get('prompt_tokens', 0)), int(uso.get('completion_tokens', 0))
    except (KeyError, IndexError, TypeError) as exc:
        raise ErroProvedor('Resposta inesperada do provedor.') from exc
