import base64

from django.conf import settings

from commex.models import ConfiguracaoGlobal, DiaAulaConfiguracao


def _get_secret() -> bytes:
    secret = getattr(settings, 'GLOBAL_SETTINGS_TOKEN_SECRET', '') or settings.SECRET_KEY
    return str(secret).encode('utf-8')


def mask_token(token: str) -> str:
    if not token:
        return ''
    if len(token) <= 8:
        return '*' * len(token)
    return f"{token[:4]}{'*' * (len(token) - 8)}{token[-4:]}"


def _xor_bytes(data: bytes, key: bytes) -> bytes:
    return bytes([b ^ key[i % len(key)] for i, b in enumerate(data)])


def encrypt_token(token: str) -> str:
    if not token:
        return ''
    raw = token.encode('utf-8')
    encoded = _xor_bytes(raw, _get_secret())
    return base64.urlsafe_b64encode(encoded).decode('ascii')


def decrypt_token(token_cipher: str) -> str:
    if not token_cipher:
        return ''
    try:
        data = base64.urlsafe_b64decode(token_cipher.encode('ascii'))
        decoded = _xor_bytes(data, _get_secret())
        return decoded.decode('utf-8')
    except Exception:
        return ''


def get_or_create_global_settings() -> ConfiguracaoGlobal:
    obj = ConfiguracaoGlobal.objects.order_by('id').first()
    if obj:
        return obj
    return ConfiguracaoGlobal.objects.create()


def save_global_settings(token_plain: str, dias):
    obj = get_or_create_global_settings()
    obj.github_token = encrypt_token((token_plain or '').strip())
    obj.save()
    obj.dias_aula.set(dias)
    return obj


def clear_token() -> ConfiguracaoGlobal:
    obj = get_or_create_global_settings()
    obj.github_token = ''
    obj.save(update_fields=['github_token', 'atualizado_em'])
    return obj


def get_plain_github_token() -> str:
    obj = get_or_create_global_settings()
    return decrypt_token(obj.github_token)


def bootstrap_dias_aula_choices():
    defaults = [
        ('SEGUNDA', 'Segunda-feira'),
        ('TERCA', 'Terca-feira'),
        ('QUARTA', 'Quarta-feira'),
        ('QUINTA', 'Quinta-feira'),
        ('SEXTA', 'Sexta-feira'),
    ]
    for codigo, label in defaults:
        DiaAulaConfiguracao.objects.get_or_create(codigo=codigo, defaults={'label': label})
