import calendar
import json
from datetime import date, timedelta

from django.http import HttpResponse
from django.shortcuts import render
from django.utils.safestring import mark_safe

from sigad_app.report_export import build_relatorio_distribuicao_xlsx


def sidebar_items():
    return [
        {'label': 'Dashboard', 'url_name': 'dashboard', 'icon': 'layout-dashboard'},
        {'label': 'Registrar Item', 'url_name': 'registrar_item', 'icon': 'package-plus'},
        {'label': 'Registrar Distribuição', 'url_name': 'registrar_distribuicao', 'icon': 'arrow-right-left'},
        {'label': 'Estoque', 'url_name': 'estoque', 'icon': 'boxes'},
        {'label': 'Beneficiários', 'url_name': 'beneficiarios', 'icon': 'users'},
        {'label': 'Relatórios', 'url_name': 'relatorios', 'icon': 'bar-chart-3'},
    ]


def base_context(active):
    return {
        'sidebar_items': sidebar_items(),
        'active_page': active,
    }


def dashboard(request):
    context = base_context('dashboard')
    context.update({
        'cards': [
            {'title': 'Total em Estoque', 'value': '1.247', 'delta': '+12.5%', 'icon': 'package', 'tone': 'blue'},
            {'title': 'Beneficiários Ativos', 'value': '342', 'delta': '+8.2%', 'icon': 'users', 'tone': 'green'},
            {'title': 'Distribuições (mês)', 'value': '156', 'delta': '+15.3%', 'icon': 'trending-up', 'tone': 'purple'},
            {'title': 'Itens Vencendo', 'value': '23', 'delta': 'Próximos 7 dias', 'icon': 'alert-circle', 'tone': 'orange'},
        ],
        'atividades': [
            {'titulo': 'Doação recebida', 'descricao': 'Arroz 5kg • João Silva', 'tempo': 'há 5 min'},
            {'titulo': 'Distribuição realizada', 'descricao': 'Feijão 1kg • undefined • Maria Santos', 'tempo': 'há 12 min'},
            {'titulo': 'Novo beneficiário', 'descricao': 'Carlos Oliveira', 'tempo': 'há 1 hora'},
            {'titulo': 'Doação recebida', 'descricao': 'Sabonete 90g • Empresa XYZ', 'tempo': 'há 2 horas'},
        ]
    })
    return render(request, 'sigad_app/dashboard.html', context)


def registrar_item(request):
    context = base_context('registrar_item')
    context['categorias'] = ['Selecione uma categoria', 'Alimentos', 'Higiene', 'Roupas']
    context['unidades'] = ['Selecione', 'pacote', 'unidade', 'litro', 'kg']
    return render(request, 'sigad_app/registrar_item.html', context)


def registrar_distribuicao(request):
    context = base_context('registrar_distribuicao')
    context['beneficiarios'] = ['Selecione um beneficiário', 'Maria Santos', 'João Silva', 'Carlos Oliveira', 'Ana Paula Costa']
    context['itens'] = ['Buscar item no estoque...', 'Arroz Branco 5kg', 'Feijão Preto 1kg', 'Sabonete 90g', 'Camiseta Tamanho M']
    return render(request, 'sigad_app/registrar_distribuicao.html', context)


def estoque(request):
    context = base_context('estoque')
    context['itens_estoque'] = [
        {'nome': 'Arroz Branco 5kg', 'categoria': 'Alimentos', 'quantidade': 150, 'unidade': 'pacote', 'validade': '14/08/2026', 'doador': 'João Silva', 'badge': 'green'},
        {'nome': 'Feijão Preto 1kg', 'categoria': 'Alimentos', 'quantidade': 95, 'unidade': 'pacote', 'validade': '19/10/2026', 'doador': 'Maria Santos', 'badge': 'green'},
        {'nome': 'Sabonete 90g', 'categoria': 'Higiene', 'quantidade': 230, 'unidade': 'unidade', 'validade': '09/03/2027', 'doador': 'Empresa XYZ', 'badge': 'blue'},
        {'nome': 'Camiseta Tamanho M', 'categoria': 'Roupas', 'quantidade': 45, 'unidade': 'unidade', 'validade': '-', 'doador': 'Doação Anônima', 'badge': 'purple'},
        {'nome': 'Óleo de Soja 900ml', 'categoria': 'Alimentos', 'quantidade': 78, 'unidade': 'litro', 'validade': '29/06/2026', 'doador': 'Carlos Oliveira', 'badge': 'green'},
        {'nome': 'Shampoo 350ml', 'categoria': 'Higiene', 'quantidade': 62, 'unidade': 'unidade', 'validade': '14/01/2027', 'doador': 'Ana Costa', 'badge': 'blue'},
    ]
    context['total_estoque'] = 660
    return render(request, 'sigad_app/estoque.html', context)


def beneficiarios(request):
    context = base_context('beneficiarios')
    context['beneficiarios_cards'] = [
        {'nome': 'Maria Santos', 'cpf': '123.456.789-00', 'telefone': '(11) 98765-4321', 'email': 'maria.santos@email.com', 'endereco': 'Rua das Flores, 123 - São Paulo, SP', 'ultima_distribuicao': '27/03/2026'},
        {'nome': 'João Silva', 'cpf': '987.654.321-00', 'telefone': '(11) 91234-5678', 'email': 'joao.silva@email.com', 'endereco': 'Av. Paulista, 456 - São Paulo, SP', 'ultima_distribuicao': '24/03/2026'},
        {'nome': 'Carlos Oliveira', 'cpf': '456.789.123-00', 'telefone': '(11) 92345-6789', 'email': 'carlos.oliveira@email.com', 'endereco': 'Rua da Esperança, 789 - São Paulo, SP', 'ultima_distribuicao': '20/03/2026'},
        {'nome': 'Ana Paula Costa', 'cpf': '321.654.987-00', 'telefone': '(11) 93456-7890', 'email': 'ana.costa@email.com', 'endereco': 'Rua do Comércio, 321 - São Paulo, SP', 'ultima_distribuicao': '18/03/2026'},
    ]
    return render(request, 'sigad_app/beneficiarios.html', context)


def _dist_mock_count(d: date) -> int:
    """Contagem demo por dia (substituir por agregação em banco quando houver modelo de distribuição)."""
    seed = d.year * 10000 + d.month * 100 + d.day
    return 4 + (seed % 15)


def _fmt_br_int(n: int) -> str:
    neg = n < 0
    s = str(abs(n))
    chunks = []
    while s:
        chunks.append(s[-3:])
        s = s[:-3]
    out = '.'.join(reversed(chunks))
    return f'-{out}' if neg else out


def _categoria_mock_unidades(categoria: str, ref: date) -> int:
    """Unidades demo por categoria no mês (substituir por agregação real)."""
    seed = sum(ord(c) for c in categoria) + ref.year * 100 + ref.month * 31
    return 24 + (seed % 120)


RELATORIO_CATEGORIAS = [
    'Alimentos',
    'Higiene',
    'Roupas',
    'Limpeza',
    'Outros',
]


def relatorios(request):
    periodo = request.GET.get('periodo', 'semanal')
    if periodo not in ('semanal', 'mensal', 'categoria'):
        periodo = 'semanal'

    today = date.today()
    dias_pt = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
    meses_pt = (
        '',
        'janeiro',
        'fevereiro',
        'março',
        'abril',
        'maio',
        'junho',
        'julho',
        'agosto',
        'setembro',
        'outubro',
        'novembro',
        'dezembro',
    )

    chart_index_axis = 'x'
    chart_legend_hint = 'Distribuições registradas por dia'
    value_label = 'distribuições'

    if periodo == 'semanal':
        start = today - timedelta(days=today.weekday())
        end = start + timedelta(days=6)
        labels = []
        values = []
        for i in range(7):
            d = start + timedelta(days=i)
            labels.append(f"{dias_pt[i]} {d.day:02d}/{d.month:02d}")
            values.append(_dist_mock_count(d))
        if start.month == end.month:
            periodo_titulo = f"{start.day:02d}–{end.day:02d} de {meses_pt[end.month]} de {end.year}"
        else:
            periodo_titulo = (
                f"{start.day:02d}/{start.month:02d} – {end.day:02d}/{end.month:02d} de {end.year}"
            )
        chart_title = 'Distribuições por dia (semana corrente)'
        chart_type = 'bar'
    elif periodo == 'mensal':
        start = date(today.year, today.month, 1)
        _, last_day = calendar.monthrange(today.year, today.month)
        end = date(today.year, today.month, last_day)
        labels = []
        values = []
        for day in range(1, last_day + 1):
            d = date(today.year, today.month, day)
            labels.append(f"{day:02d}")
            values.append(_dist_mock_count(d))
        periodo_titulo = f"{meses_pt[today.month].title()} {today.year}"
        chart_title = 'Distribuições por dia no mês'
        chart_type = 'line'
    else:
        start = date(today.year, today.month, 1)
        _, last_day = calendar.monthrange(today.year, today.month)
        end = date(today.year, today.month, last_day)
        labels = list(RELATORIO_CATEGORIAS)
        values = [_categoria_mock_unidades(cat, today) for cat in labels]
        periodo_titulo = f"Categorias — {meses_pt[today.month].title()} {today.year}"
        chart_title = 'Unidades distribuídas por categoria (mês corrente)'
        chart_type = 'bar'
        chart_index_axis = 'y'
        chart_legend_hint = 'Total estimado de unidades no mês, por categoria'
        value_label = 'unidades'

    total_distrib = sum(values)
    itens_mov = total_distrib * 11 + today.day * 3
    beneficiarios_atend = min(220, max(12, total_distrib * 2 + 8))

    tipo_relatorio = {
        'semanal': 'Semanal',
        'mensal': 'Mensal',
        'categoria': 'Por categoria',
    }.get(periodo, periodo)
    col_ref = 'Categoria' if periodo == 'categoria' else 'Referência'
    col_qtd = 'Unidades distribuídas' if periodo == 'categoria' else 'Quantidade'

    if request.GET.get('export') == 'xlsx':
        xbuf = build_relatorio_distribuicao_xlsx(
            periodo_titulo=periodo_titulo,
            tipo_label=tipo_relatorio,
            col_ref=col_ref,
            col_qtd=col_qtd,
            labels=labels,
            values=values,
            total=total_distrib,
        )
        response = HttpResponse(
            xbuf.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        fname = f'sigad-relatorio-{periodo}-{today.isoformat()}.xlsx'
        response['Content-Disposition'] = f'attachment; filename="{fname}"'
        return response

    if periodo == 'categoria':
        total_unidades = total_distrib
        n_cats = len([v for v in values if v > 0])
        idx_max = max(range(len(values)), key=lambda i: values[i])
        destaque_nome = labels[idx_max]
        destaque_val = values[idx_max]
        resumo_cards = [
            {
                'title': 'Categorias no relatório',
                'value': _fmt_br_int(n_cats),
                'delta': 'com movimentação no mês',
                'icon': 'layers',
                'tone': 'blue',
            },
            {
                'title': 'Unidades no mês',
                'value': _fmt_br_int(total_unidades),
                'delta': 'soma por categoria',
                'icon': 'arrow-right-left',
                'tone': 'green',
            },
            {
                'title': 'Categoria em destaque',
                'value': _fmt_br_int(destaque_val),
                'delta': destaque_nome[:42] + ('…' if len(destaque_nome) > 42 else ''),
                'icon': 'trending-up',
                'tone': 'purple',
            },
        ]
    else:
        resumo_cards = [
            {
                'title': 'Distribuições',
                'value': _fmt_br_int(total_distrib),
                'delta': 'registros no período',
                'icon': 'arrow-right-left',
                'tone': 'blue',
            },
            {
                'title': 'Itens movimentados',
                'value': _fmt_br_int(itens_mov),
                'delta': 'unidades (estimativa)',
                'icon': 'package',
                'tone': 'green',
            },
            {
                'title': 'Beneficiários',
                'value': _fmt_br_int(beneficiarios_atend),
                'delta': 'atendimentos no período',
                'icon': 'users',
                'tone': 'purple',
            },
        ]

    context = base_context('relatorios')
    context.update(
        {
            'periodo': periodo,
            'periodo_titulo': periodo_titulo,
            'chart_title': chart_title,
            'chart_type': chart_type,
            'chart_index_axis': chart_index_axis,
            'chart_legend_hint': chart_legend_hint,
            'value_label': value_label,
            'today': today.strftime('%d/%m/%Y'),
            'range_inicio': start.strftime('%d/%m/%Y'),
            'range_fim': end.strftime('%d/%m/%Y'),
            'resumo_cards': resumo_cards,
            'chart_labels_json': mark_safe(json.dumps(labels)),
            'chart_values_json': mark_safe(json.dumps(values)),
        }
    )
    return render(request, 'sigad_app/relatorios.html', context)
