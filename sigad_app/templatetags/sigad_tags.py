from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def url_pagina(context, numero):
    """
    Gera a URL de uma página preservando todos os parâmetros GET ativos
    (filtros do Django Filter, busca manual, etc.), trocando apenas o
    parâmetro 'page'.

    Uso no template:
        {% load sigad_tags %}
        {% url_pagina 3 %}          → ?nome=arroz&categoria=Alimentos&page=3
        {% url_pagina page_obj.next_page_number %}
    """
    request = context.get('request')
    if request is None:
        return f'?page={numero}'

    params = request.GET.copy()
    params['page'] = numero
    return f'?{params.urlencode()}'
