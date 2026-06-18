SIDEBAR_ITEMS = [
    {'label': 'Dashboard', 'url_name': 'dashboard', 'icon': 'layout-dashboard'},
    {'label': 'Cadastrar Item', 'url_name': 'item_estoque_create', 'icon': 'package-plus'},
    {'label': 'Cadastrar Distribuição', 'url_name': 'distribuicao_create', 'icon': 'arrow-right-left'},
    {'label': 'Estoque', 'url_name': 'item_estoque_list', 'icon': 'boxes'},
    {'label': 'Beneficiários', 'url_name': 'beneficiario_list', 'icon': 'users'},
    {'label': 'Linhas de Distribuição', 'url_name': 'linha_distribuicao_list', 'icon': 'list'},
]

_ACTIVE_PAGE_MAP = {
    'beneficiario': 'beneficiario_list',
    'item_estoque': 'item_estoque_list',
    'distribuicao': 'distribuicao_list',
    'linha_distribuicao': 'linha_distribuicao_list',
}


def _resolve_active_page(url_name: str) -> str:
    if not url_name:
        return ''
    for prefix, list_name in _ACTIVE_PAGE_MAP.items():
        if url_name == prefix or url_name.startswith(f'{prefix}_'):
            return list_name
    return url_name


def sigad_nav(request):
    url_name = getattr(getattr(request, 'resolver_match', None), 'url_name', '') or ''
    return {
        'sidebar_items': SIDEBAR_ITEMS,
        'active_page': _resolve_active_page(url_name),
    }
