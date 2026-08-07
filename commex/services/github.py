from urllib.parse import urlparse

import requests


class GitHubValidationError(Exception):
    pass


def validate_github_url(url: str, *, kind: str = 'repository') -> str:
    if not isinstance(url, str) or not url.strip():
        raise GitHubValidationError('Informe um link do GitHub.')

    parsed = urlparse(url)
    if parsed.scheme not in {'http', 'https'} or parsed.netloc != 'github.com':
        raise GitHubValidationError('O link informado deve apontar para o GitHub.')

    path_parts = [part for part in parsed.path.split('/') if part]
    if kind == 'repository':
        if len(path_parts) < 2:
            raise GitHubValidationError('O link do repositório deve seguir o formato https://github.com/owner/repo.')
    else:
        if len(path_parts) < 1:
            raise GitHubValidationError('O link da organização/conta deve seguir o formato https://github.com/owner.')

    try:
        response = requests.get(url, timeout=5)
    except requests.RequestException as exc:
        raise GitHubValidationError('Não foi possível validar o link informado no momento.') from exc

    if response.status_code != 200:
        raise GitHubValidationError('O link informado não corresponde a uma organização ou repositório GitHub válido.')

    return url


def normalize_owner_from_url(url: str) -> str:
    parsed = urlparse(url)
    parts = [part for part in parsed.path.split('/') if part]
    if not parts:
        raise GitHubValidationError('O link informado não possui um owner válido.')
    return parts[0]
