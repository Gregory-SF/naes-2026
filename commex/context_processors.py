from django.conf import settings


def permissoes(request):
    """Expõe nos templates se o usuário pode escrever (grupo Coordenadores ou superusuário)."""
    user = getattr(request, 'user', None)
    eh_coordenador = bool(
        user
        and user.is_authenticated
        and (user.is_superuser or user.groups.filter(name=settings.GRUPO_COORDENADORES).exists())
    )
    return {'eh_coordenador': eh_coordenador}
