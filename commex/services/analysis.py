from datetime import datetime

import requests
from django.utils import timezone

from commex.models import Aluno, Branch, CommitAnalisado, ExecucaoAnalise, StatusExecucaoAnalise
from commex.services.global_settings import get_plain_github_token


class AnalysisServiceError(Exception):
    pass


def _headers() -> dict:
    token = get_plain_github_token()
    if not token:
        raise AnalysisServiceError('Token do GitHub nao configurado.')
    return {
        'Accept': 'application/vnd.github+json',
        'Authorization': f'Bearer {token}',
        'X-GitHub-Api-Version': '2022-11-28',
    }


def _owner_repo_from_link(link: str):
    parts = [p for p in link.split('/') if p]
    if len(parts) < 2:
        raise AnalysisServiceError('Link de repositorio invalido.')
    return parts[-2], parts[-1]


def fetch_remote_branches(repo_link: str):
    owner, repo = _owner_repo_from_link(repo_link)
    url = f'https://api.github.com/repos/{owner}/{repo}/branches?per_page=100'
    resp = requests.get(url, headers=_headers(), timeout=15)
    if resp.status_code != 200:
        raise AnalysisServiceError('Nao foi possivel buscar branches no GitHub.')
    data = resp.json()
    return [item.get('name') for item in data if item.get('name')]


def persist_branch_names(repositorio, names):
    created = 0
    for name in names:
        _, was_created = Branch.objects.get_or_create(repositorio=repositorio, nome=name)
        if was_created:
            created += 1
    return created


def _parse_github_date(value: str):
    return datetime.strptime(value, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)


def _associate_aluno(author_login: str):
    if not author_login:
        return None
    return Aluno.objects.filter(github_nickname__iexact=author_login).first()


def import_commits_for_execution(execucao: ExecucaoAnalise):
    execucao.status = StatusExecucaoAnalise.PROCESSANDO
    execucao.progresso_percentual = 0
    execucao.erro = ''
    execucao.save(update_fields=['status', 'progresso_percentual', 'erro'])

    owner, repo = _owner_repo_from_link(execucao.repositorio.link)
    page = 1
    imported = 0
    base_url = f'https://api.github.com/repos/{owner}/{repo}/commits'

    params = {
        'sha': execucao.branch.nome,
        'since': execucao.data_inicio.isoformat() + 'T00:00:00Z',
        'until': execucao.data_fim.isoformat() + 'T23:59:59Z',
        'per_page': 100,
    }

    try:
        while True:
            params['page'] = page
            resp = requests.get(base_url, headers=_headers(), params=params, timeout=20)
            if resp.status_code == 403:
                raise AnalysisServiceError('Limite de requisicoes GitHub atingido.')
            if resp.status_code != 200:
                raise AnalysisServiceError('Erro ao importar commits do GitHub.')

            commits = resp.json()
            if not commits:
                break

            for item in commits:
                sha = item.get('sha', '')
                commit_data = item.get('commit', {})
                author_data = commit_data.get('author') or {}
                author_api = item.get('author') or {}
                author_login = author_api.get('login', '')
                when = author_data.get('date')
                if not sha or not when:
                    continue

                CommitAnalisado.objects.get_or_create(
                    execucao=execucao,
                    sha=sha,
                    defaults={
                        'mensagem': commit_data.get('message', ''),
                        'data_commit': _parse_github_date(when),
                        'autor_nome': author_data.get('name', '') or '',
                        'autor_email': author_data.get('email', '') or '',
                        'autor_login': author_login or '',
                        'url': item.get('html_url', ''),
                        'aluno': _associate_aluno(author_login),
                    },
                )
                imported += 1

            page += 1
            execucao.progresso_percentual = min(95, 15 + page * 5)
            execucao.save(update_fields=['progresso_percentual'])

        execucao.progresso_percentual = 100
        execucao.status = StatusExecucaoAnalise.CONCLUIDA
        execucao.finalizado_em = timezone.now()
        execucao.save(update_fields=['progresso_percentual', 'status', 'finalizado_em'])
        return imported
    except Exception as exc:
        execucao.status = StatusExecucaoAnalise.FALHA
        execucao.erro = str(exc)
        execucao.finalizado_em = timezone.now()
        execucao.save(update_fields=['status', 'erro', 'finalizado_em'])
        raise
