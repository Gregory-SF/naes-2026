from django.contrib.auth.decorators import login_required, user_passes_test


def group_required(*group_names):
    """Permite acesso apenas a usuarios autenticados que pertencam a um dos grupos informados
    (superusuarios sempre tem acesso)."""

    def in_groups(user):
        return user.is_superuser or user.groups.filter(name__in=group_names).exists()

    def decorator(view_func):
        return login_required(user_passes_test(in_groups)(view_func))

    return decorator
