SIDEBAR_ITEMS = [
    {'label': 'Dashboard', 'url_name': 'dashboard', 'icon': 'layout-dashboard'},
    {'label': 'Registrar Item', 'url_name': 'registrar_item', 'icon': 'package-plus'},
    {'label': 'Registrar Distribuição', 'url_name': 'registrar_distribuicao', 'icon': 'arrow-right-left'},
    {'label': 'Estoque', 'url_name': 'estoque', 'icon': 'boxes'},
    {'label': 'Beneficiários', 'url_name': 'beneficiario_list', 'icon': 'users'},
    {'label': 'Beneficiados', 'url_name': 'beneficiado_list', 'icon': 'heart-handshake'},
    {'label': 'Distribuições', 'url_name': 'distribuicao_list', 'icon': 'list'},
    {'label': 'Relatórios', 'url_name': 'relatorios', 'icon': 'bar-chart-2'},
]

_ACTIVE_PAGE_MAP = {
    'beneficiario': 'beneficiario_list',
    'beneficiado': 'beneficiado_list',
    'item_estoque': 'item_estoque_list',
    'distribuicao': 'distribuicao_list',
    'linha_distribuicao': 'distribuicao_list',
    'estoque': 'estoque',
    'registrar_item': 'registrar_item',
    'registrar_distribuicao': 'registrar_distribuicao',
    'relatorios': 'relatorios',
}


def _resolve_active_page(url_name: str) -> str:
    if not url_name:
        return ''
    if url_name in _ACTIVE_PAGE_MAP:
        return _ACTIVE_PAGE_MAP[url_name]
    for prefix, list_name in _ACTIVE_PAGE_MAP.items():
        if url_name.startswith(f'{prefix}_'):
            return list_name
    return url_name


def sigad_nav(request):
    url_name = getattr(getattr(request, 'resolver_match', None), 'url_name', '') or ''
    return {
        'sidebar_items': SIDEBAR_ITEMS,
        'active_page': _resolve_active_page(url_name),
    }
