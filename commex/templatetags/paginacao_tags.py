from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def url_params(context, **kwargs):
    """Reescreve a querystring atual trocando/removendo os parâmetros informados.

    Uso na paginação, preservando os filtros da busca:
        <a href="?{% url_params page=page_obj.next_page_number %}">Próxima</a>

    Um valor vazio ou None remove o parâmetro. Parâmetros multivalorados
    (ex.: ?status=A&status=B) são mantidos integralmente.
    """
    params = context['request'].GET.copy()
    for chave, valor in kwargs.items():
        if valor in (None, ''):
            params.pop(chave, None)
        else:
            params[chave] = valor
    return params.urlencode()
