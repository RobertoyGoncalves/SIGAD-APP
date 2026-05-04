import calendar
import json
from datetime import date, timedelta

from django.contrib import messages
from django.db import transaction
from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncDate
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.safestring import mark_safe

from sigad_app.forms import BeneficiarioForm, ItemEstoqueForm
from sigad_app.models import Beneficiario, Distribuicao, ItemEstoque, LinhaDistribuicao
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


BADGE_POR_CATEGORIA = {
    'Alimentos': 'green',
    'Higiene': 'blue',
    'Roupas': 'purple',
    'Limpeza': 'blue',
    'Outros': 'purple',
}


def _badge(categoria):
    return BADGE_POR_CATEGORIA.get(categoria, 'blue')


def _fmt_br_int(n: int) -> str:
    neg = n < 0
    s = str(abs(n))
    chunks = []
    while s:
        chunks.append(s[-3:])
        s = s[:-3]
    out = '.'.join(reversed(chunks))
    return f'-{out}' if neg else out


def _human_tempo(dt):
    if not dt:
        return ''
    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt, timezone.get_current_timezone())
    now = timezone.now()
    diff = now - dt
    if diff.days > 7:
        return timezone.localtime(dt).strftime('%d/%m/%Y %H:%M')
    if diff.days >= 1:
        return f'há {diff.days} dia(s)'
    sec = int(diff.total_seconds())
    if sec >= 3600:
        return f'há {sec // 3600} hora(s)'
    if sec >= 60:
        return f'há {sec // 60} min'
    return 'agora'


def dashboard(request):
    today = timezone.localdate()
    fim_validade = today + timedelta(days=7)

    total_qtd = (
        ItemEstoque.objects.aggregate(s=Sum('quantidade'))['s'] or 0
    )
    n_benef = Beneficiario.objects.count()
    inicio_mes = today.replace(day=1)
    dist_mes = Distribuicao.objects.filter(registrado_em__date__gte=inicio_mes).count()
    vencendo = ItemEstoque.objects.filter(
        validade__isnull=False,
        validade__gte=today,
        validade__lte=fim_validade,
        quantidade__gt=0,
    ).count()

    cards = [
        {
            'title': 'Total em Estoque',
            'value': _fmt_br_int(int(total_qtd)),
            'delta': 'unidades somadas',
            'icon': 'package',
            'tone': 'blue',
        },
        {
            'title': 'Beneficiários',
            'value': _fmt_br_int(n_benef),
            'delta': 'cadastrados',
            'icon': 'users',
            'tone': 'green',
        },
        {
            'title': 'Distribuições (mês)',
            'value': _fmt_br_int(dist_mes),
            'delta': inicio_mes.strftime('%m/%Y'),
            'icon': 'trending-up',
            'tone': 'purple',
        },
        {
            'title': 'Itens vencendo',
            'value': _fmt_br_int(vencendo),
            'delta': 'próximos 7 dias',
            'icon': 'alert-circle',
            'tone': 'orange',
        },
    ]

    atividades = []
    for it in ItemEstoque.objects.order_by('-criado_em')[:8]:
        atividades.append(
            {
                'titulo': 'Item cadastrado',
                'descricao': f'{it.nome} • {it.doador or "—"}',
                'tempo': _human_tempo(it.criado_em),
                'ts': it.criado_em,
            }
        )
    for b in Beneficiario.objects.order_by('-criado_em')[:8]:
        atividades.append(
            {
                'titulo': 'Beneficiário cadastrado',
                'descricao': b.nome,
                'tempo': _human_tempo(b.criado_em),
                'ts': b.criado_em,
            }
        )
    for d in Distribuicao.objects.select_related('beneficiario').order_by('-registrado_em')[:8]:
        n_linhas = d.linhas.count()
        atividades.append(
            {
                'titulo': 'Distribuição registrada',
                'descricao': f'{d.beneficiario.nome} • {n_linhas} tipo(s) de item',
                'tempo': _human_tempo(d.registrado_em),
                'ts': d.registrado_em,
            }
        )
    atividades.sort(key=lambda x: x['ts'], reverse=True)
    atividades = atividades[:12]
    for a in atividades:
        a.pop('ts', None)

    context = base_context('dashboard')
    context.update({'cards': cards, 'atividades': atividades})
    return render(request, 'sigad_app/dashboard.html', context)


def registrar_item(request):
    if request.method == 'POST':
        form = ItemEstoqueForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Item cadastrado no estoque.')
            return redirect('registrar_item')
        messages.error(request, 'Corrija os erros no formulário.')
    else:
        form = ItemEstoqueForm()

    context = base_context('registrar_item')
    context['form'] = form
    return render(request, 'sigad_app/registrar_item.html', context)


def registrar_distribuicao(request):
    if request.method == 'POST':
        raw = (request.POST.get('linhas_json') or '').strip()
        ben_id = request.POST.get('beneficiario_id')
        try:
            ben_id = int(ben_id)
        except (TypeError, ValueError):
            ben_id = None
        try:
            linhas = json.loads(raw) if raw else []
        except json.JSONDecodeError:
            linhas = []
        if not ben_id:
            messages.error(request, 'Selecione um beneficiário.')
        elif not isinstance(linhas, list) or not linhas:
            messages.error(request, 'Adicione pelo menos um item à distribuição.')
        else:
            try:
                with transaction.atomic():
                    ben = Beneficiario.objects.select_for_update().get(pk=ben_id)
                    dist = Distribuicao.objects.create(beneficiario=ben)
                    for linha in linhas:
                        item_id = int(linha['item_id'])
                        qtd = int(linha['quantidade'])
                        if qtd < 1:
                            raise ValueError('Quantidade inválida.')
                        item = ItemEstoque.objects.select_for_update().get(pk=item_id)
                        if item.quantidade < qtd:
                            raise ValueError(
                                f'Estoque insuficiente para "{item.nome}" (disponível: {item.quantidade}).'
                            )
                        item.quantidade -= qtd
                        item.save(update_fields=['quantidade'])
                        LinhaDistribuicao.objects.create(
                            distribuicao=dist,
                            item_estoque=item,
                            quantidade=qtd,
                        )
                    hoje = timezone.localdate()
                    ben.ultima_distribuicao = hoje
                    ben.save(update_fields=['ultima_distribuicao'])
                messages.success(request, 'Distribuição registrada e estoque atualizado.')
                return redirect('registrar_distribuicao')
            except Beneficiario.DoesNotExist:
                messages.error(request, 'Beneficiário não encontrado.')
            except ItemEstoque.DoesNotExist:
                messages.error(request, 'Item de estoque não encontrado.')
            except ValueError as e:
                messages.error(request, str(e))

    itens_qs = ItemEstoque.objects.filter(quantidade__gt=0).order_by('nome')
    itens_opts = [{'id': i.id, 'label': f'{i.nome} ({i.quantidade} {i.unidade})'} for i in itens_qs]
    beneficiarios_opts = list(
        Beneficiario.objects.order_by('nome').values('id', 'nome')
    )

    context = base_context('registrar_distribuicao')
    context.update(
        {
            'beneficiarios_opts': beneficiarios_opts,
            'itens_opts': itens_opts,
            'itens_opts_json': mark_safe(json.dumps(itens_opts)),
        }
    )
    return render(request, 'sigad_app/registrar_distribuicao.html', context)


def estoque(request):
    q = (request.GET.get('q') or '').strip()
    cat = (request.GET.get('categoria') or '').strip()
    qs = ItemEstoque.objects.all().order_by('nome')
    if q:
        qs = qs.filter(Q(nome__icontains=q) | Q(doador__icontains=q))
    if cat and cat in dict(ItemEstoque.CATEGORIAS):
        qs = qs.filter(categoria=cat)

    itens_estoque = []
    for item in qs:
        vd = item.validade.strftime('%d/%m/%Y') if item.validade else '—'
        itens_estoque.append(
            {
                'nome': item.nome,
                'categoria': item.get_categoria_display(),
                'quantidade': item.quantidade,
                'unidade': item.unidade,
                'validade': vd,
                'doador': item.doador,
                'badge': _badge(item.categoria),
            }
        )
    total = sum(i['quantidade'] for i in itens_estoque)

    context = base_context('estoque')
    context.update(
        {
            'itens_estoque': itens_estoque,
            'total_estoque': total,
            'filtro_q': q,
            'filtro_categoria': cat,
            'categorias_filtro': ItemEstoque.CATEGORIAS,
        }
    )
    return render(request, 'sigad_app/estoque.html', context)


def beneficiarios(request):
    if request.method == 'POST':
        form = BeneficiarioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Beneficiário cadastrado.')
            return redirect('beneficiarios')
        messages.error(request, 'Corrija os erros no formulário.')
    else:
        form = BeneficiarioForm()

    q = (request.GET.get('q') or '').strip()
    qs = Beneficiario.objects.all().order_by('nome')
    if q:
        qs = qs.filter(
            Q(nome__icontains=q)
            | Q(cpf__icontains=q)
            | Q(email__icontains=q)
            | Q(telefone__icontains=q)
        )

    beneficiarios_cards = []
    for b in qs:
        ud = (
            b.ultima_distribuicao.strftime('%d/%m/%Y')
            if b.ultima_distribuicao
            else '—'
        )
        beneficiarios_cards.append(
            {
                'nome': b.nome,
                'cpf': b.cpf,
                'telefone': b.telefone,
                'email': b.email,
                'endereco': b.endereco,
                'ultima_distribuicao': ud,
            }
        )

    context = base_context('beneficiarios')
    context.update({'beneficiarios_cards': beneficiarios_cards, 'form': form, 'filtro_q': q})
    return render(request, 'sigad_app/beneficiarios.html', context)


def _relatorio_semanal(today):
    start = today - timedelta(days=today.weekday())
    end = start + timedelta(days=6)
    dias_pt = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
    labels = []
    for i in range(7):
        d = start + timedelta(days=i)
        labels.append(f"{dias_pt[i]} {d.day:02d}/{d.month:02d}")

    tz = timezone.get_current_timezone()
    qs = (
        Distribuicao.objects.filter(registrado_em__date__gte=start, registrado_em__date__lte=end)
        .annotate(day=TruncDate('registrado_em', tzinfo=tz))
        .values('day')
        .annotate(c=Count('id'))
    )
    por_dia = {row['day']: row['c'] for row in qs if row['day']}
    values = []
    for i in range(7):
        d = start + timedelta(days=i)
        values.append(por_dia.get(d, 0))

    if start.month == end.month:
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
        periodo_titulo = f"{start.day:02d}–{end.day:02d} de {meses_pt[end.month]} de {end.year}"
    else:
        periodo_titulo = (
            f"{start.day:02d}/{start.month:02d} – {end.day:02d}/{end.month:02d} de {end.year}"
        )
    return labels, values, start, end, periodo_titulo


def _relatorio_mensal(today):
    start = date(today.year, today.month, 1)
    _, last_day = calendar.monthrange(today.year, today.month)
    end = date(today.year, today.month, last_day)
    labels = [f'{d:02d}' for d in range(1, last_day + 1)]

    tz = timezone.get_current_timezone()
    qs = (
        Distribuicao.objects.filter(
            registrado_em__date__gte=start,
            registrado_em__date__lte=end,
        )
        .annotate(day=TruncDate('registrado_em', tzinfo=tz))
        .values('day')
        .annotate(c=Count('id'))
    )
    por_dia = {row['day'].day: row['c'] for row in qs if row['day']}
    values = [por_dia.get(d, 0) for d in range(1, last_day + 1)]

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
    periodo_titulo = f"{meses_pt[today.month].title()} {today.year}"
    return labels, values, start, end, periodo_titulo


def _relatorio_categoria(today):
    start = date(today.year, today.month, 1)
    _, last_day = calendar.monthrange(today.year, today.month)
    end = date(today.year, today.month, last_day)
    labels = [c[0] for c in ItemEstoque.CATEGORIAS]
    qs = (
        LinhaDistribuicao.objects.filter(
            distribuicao__registrado_em__date__gte=start,
            distribuicao__registrado_em__date__lte=end,
        )
        .values('item_estoque__categoria')
        .annotate(total=Sum('quantidade'))
    )
    por_cat = {row['item_estoque__categoria']: int(row['total'] or 0) for row in qs}
    values = [por_cat.get(cat, 0) for cat in labels]

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
    periodo_titulo = f"Categorias — {meses_pt[today.month].title()} {today.year}"
    return labels, values, start, end, periodo_titulo


def relatorios(request):
    periodo = request.GET.get('periodo', 'semanal')
    if periodo not in ('semanal', 'mensal', 'categoria'):
        periodo = 'semanal'

    today = timezone.localdate()

    chart_index_axis = 'x'
    chart_legend_hint = 'Distribuições registradas por dia'
    value_label = 'distribuições'

    if periodo == 'semanal':
        labels, values, start, end, periodo_titulo = _relatorio_semanal(today)
        chart_title = 'Distribuições por dia (semana corrente)'
        chart_type = 'bar'
    elif periodo == 'mensal':
        labels, values, start, end, periodo_titulo = _relatorio_mensal(today)
        chart_title = 'Distribuições por dia no mês'
        chart_type = 'line'
    else:
        labels, values, start, end, periodo_titulo = _relatorio_categoria(today)
        chart_title = 'Unidades distribuídas por categoria (mês corrente)'
        chart_type = 'bar'
        chart_index_axis = 'y'
        chart_legend_hint = 'Soma de unidades retiradas do estoque no mês'
        value_label = 'unidades'

    total_distrib = sum(values)
    n_linhas_mes = LinhaDistribuicao.objects.filter(
        distribuicao__registrado_em__date__gte=start,
        distribuicao__registrado_em__date__lte=end,
    ).aggregate(s=Sum('quantidade'))['s'] or 0
    n_linhas_mes = int(n_linhas_mes)
    dist_count = Distribuicao.objects.filter(
        registrado_em__date__gte=start,
        registrado_em__date__lte=end,
    ).count()
    beneficiarios_atend = (
        Distribuicao.objects.filter(
            registrado_em__date__gte=start,
            registrado_em__date__lte=end,
        )
        .values('beneficiario')
        .distinct()
        .count()
    )

    tipo_relatorio = {
        'semanal': 'Semanal',
        'mensal': 'Mensal',
        'categoria': 'Por categoria',
    }.get(periodo, periodo)
    col_ref = 'Categoria' if periodo == 'categoria' else 'Referência'
    col_qtd = 'Unidades distribuídas' if periodo == 'categoria' else 'Quantidade (distribuições)'

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
        n_cats = sum(1 for v in values if v > 0)
        idx_max = max(range(len(values)), key=lambda i: values[i]) if values else 0
        destaque_nome = labels[idx_max] if labels else '—'
        destaque_val = values[idx_max] if values else 0
        resumo_cards = [
            {
                'title': 'Categorias com saída',
                'value': _fmt_br_int(n_cats),
                'delta': 'no mês',
                'icon': 'layers',
                'tone': 'blue',
            },
            {
                'title': 'Unidades distribuídas',
                'value': _fmt_br_int(n_linhas_mes),
                'delta': 'soma das linhas',
                'icon': 'arrow-right-left',
                'tone': 'green',
            },
            {
                'title': 'Categoria em destaque',
                'value': _fmt_br_int(destaque_val),
                'delta': destaque_nome[:42],
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
                'title': 'Unidades movimentadas',
                'value': _fmt_br_int(n_linhas_mes),
                'delta': 'itens saídos do estoque',
                'icon': 'package',
                'tone': 'green',
            },
            {
                'title': 'Beneficiários atendidos',
                'value': _fmt_br_int(beneficiarios_atend),
                'delta': 'distintos no período',
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
