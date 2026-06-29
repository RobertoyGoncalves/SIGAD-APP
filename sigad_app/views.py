import json
from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Q, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)

from sigad_app.forms import BeneficiadoForm, BeneficiarioForm, ItemEstoqueForm
from sigad_app.models import (
    Beneficiado,
    Beneficiario,
    Distribuicao,
    ItemEstoque,
    LinhaDistribuicao,
)
from sigad_app.report_export import build_relatorio_distribuicao_xlsx


# ─── Páginas públicas ─────────────────────────────────────────────────────────

class Landing(TemplateView):
    template_name = 'sigad_app/landing.html'


# ─── Dashboard ───────────────────────────────────────────────────────────────

class Dashboard(LoginRequiredMixin, TemplateView):
    template_name = 'sigad_app/dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['cards'] = [
            {
                'title': 'Itens no Estoque',
                'value': ItemEstoque.objects.count(),
                'delta': 'Total de itens cadastrados',
                'icon': 'box-seam',
                'tone': 'tone-blue',
            },
            {
                'title': 'Beneficiários',
                'value': Beneficiario.objects.count(),
                'delta': 'Quem doa',
                'icon': 'users',
                'tone': 'tone-green',
            },
            {
                'title': 'Beneficiados',
                'value': Beneficiado.objects.count(),
                'delta': 'Quem recebe',
                'icon': 'heart-handshake',
                'tone': 'tone-purple',
            },
            {
                'title': 'Distribuições',
                'value': Distribuicao.objects.count(),
                'delta': 'Total registrado',
                'icon': 'arrow-right-left',
                'tone': 'tone-orange',
            },
        ]
        atividades = []
        for d in Distribuicao.objects.select_related('beneficiado').order_by('-registrado_em')[:5]:
            atividades.append({
                'titulo': f'Distribuição #{d.pk}',
                'descricao': f'Para {d.beneficiado.nome}',
                'tempo': d.registrado_em.strftime('%d/%m/%Y %H:%M'),
            })
        for i in ItemEstoque.objects.select_related('beneficiario').order_by('-criado_em')[:5]:
            desc = f'{i.quantidade} {i.unidade}'
            if i.beneficiario:
                desc += f' — {i.beneficiario.nome}'
            atividades.append({
                'titulo': f'Doação recebida: {i.nome}',
                'descricao': desc,
                'tempo': i.criado_em.strftime('%d/%m/%Y %H:%M'),
            })
        atividades.sort(key=lambda x: x['tempo'], reverse=True)
        ctx['atividades'] = atividades[:8]
        return ctx


# ─── Beneficiário (quem DOA) ─────────────────────────────────────────────────

@login_required
def beneficiario_list(request):
    q = request.GET.get('q', '').strip()
    qs = Beneficiario.objects.prefetch_related('itens_doados').all()
    if q:
        qs = qs.filter(nome__icontains=q)

    if request.method == 'POST':
        form = BeneficiarioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Beneficiário cadastrado com sucesso.')
            return redirect('beneficiario_list')
    else:
        form = BeneficiarioForm()

    beneficiarios_data = []
    for ben in qs:
        itens = list(ben.itens_doados.order_by('-criado_em'))
        beneficiarios_data.append({
            'obj': ben,
            'itens': itens,
            'total_doacoes': len(itens),
            'total_unidades': sum(i.quantidade for i in itens),
        })

    return render(request, 'sigad_app/beneficiario_list.html', {
        'beneficiarios_data': beneficiarios_data,
        'filtro_q': q,
        'form': form,
    })


class BeneficiarioUpdate(LoginRequiredMixin, UpdateView):
    model = Beneficiario
    form_class = BeneficiarioForm
    template_name = 'sigad_app/form.html'
    success_url = reverse_lazy('beneficiario_list')
    extra_context = {'titulo': 'Editar Beneficiário', 'botao': 'Atualizar'}


class BeneficiarioDelete(LoginRequiredMixin, DeleteView):
    model = Beneficiario
    template_name = 'sigad_app/form.html'
    success_url = reverse_lazy('beneficiario_list')
    extra_context = {'titulo': 'Excluir Beneficiário', 'botao': 'Confirmar exclusão'}


# ─── Beneficiado (quem RECEBE) ────────────────────────────────────────────────

class BeneficiadoCreate(LoginRequiredMixin, CreateView):
    model = Beneficiado
    form_class = BeneficiadoForm
    template_name = 'sigad_app/form.html'
    success_url = reverse_lazy('beneficiado_list')
    extra_context = {'titulo': 'Cadastrar Beneficiado', 'botao': 'Salvar'}

    def form_valid(self, form):
        messages.success(self.request, 'Beneficiado cadastrado com sucesso.')
        return super().form_valid(form)


class BeneficiadoList(LoginRequiredMixin, ListView):
    model = Beneficiado
    template_name = 'sigad_app/beneficiado_list.html'
    context_object_name = 'beneficiados'

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(
                Q(nome__icontains=q) | Q(email__icontains=q) | Q(telefone__icontains=q)
            )
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['filtro_q'] = self.request.GET.get('q', '')
        return ctx


class BeneficiadoDetail(LoginRequiredMixin, DetailView):
    model = Beneficiado
    template_name = 'sigad_app/beneficiado_detail.html'
    context_object_name = 'beneficiado'


class BeneficiadoUpdate(LoginRequiredMixin, UpdateView):
    model = Beneficiado
    form_class = BeneficiadoForm
    template_name = 'sigad_app/form.html'
    success_url = reverse_lazy('beneficiado_list')
    extra_context = {'titulo': 'Editar Beneficiado', 'botao': 'Atualizar'}


class BeneficiadoDelete(LoginRequiredMixin, DeleteView):
    model = Beneficiado
    template_name = 'sigad_app/form.html'
    success_url = reverse_lazy('beneficiado_list')
    extra_context = {'titulo': 'Excluir Beneficiado', 'botao': 'Confirmar exclusão'}


# ─── Estoque ──────────────────────────────────────────────────────────────────

@login_required
def registrar_item(request):
    if request.method == 'POST':
        form = ItemEstoqueForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.quantidade_doada = item.quantidade
            item.save()
            messages.success(request, 'Item cadastrado no estoque com sucesso.')
            return redirect('item_estoque_list')
    else:
        form = ItemEstoqueForm()
    return render(request, 'sigad_app/registrar_item.html', {'form': form})


@login_required
def estoque(request):
    q = request.GET.get('q', '').strip()
    categoria = request.GET.get('categoria', '').strip()
    qs = ItemEstoque.objects.select_related('beneficiario').all()
    if q:
        qs = qs.filter(
            Q(nome__icontains=q) | Q(beneficiario__nome__icontains=q)
        ).distinct()
    if categoria:
        qs = qs.filter(categoria=categoria)

    badge_map = {
        'Alimentos': 'green',
        'Higiene': 'blue',
        'Roupas': 'purple',
        'Limpeza': 'blue',
        'Outros': 'neutral',
    }
    itens = list(qs)
    for item in itens:
        item.badge = badge_map.get(item.categoria, 'neutral')

    return render(request, 'sigad_app/estoque.html', {
        'itens_estoque': itens,
        'filtro_q': q,
        'filtro_categoria': categoria,
        'categorias_filtro': ItemEstoque.CATEGORIAS,
        'total_estoque': sum(i.quantidade for i in itens),
    })


class ItemEstoqueList(LoginRequiredMixin, ListView):
    model = ItemEstoque
    template_name = 'sigad_app/item_estoque_list.html'
    context_object_name = 'itens_estoque'
    queryset = ItemEstoque.objects.select_related('beneficiario')


class ItemEstoqueUpdate(LoginRequiredMixin, UpdateView):
    model = ItemEstoque
    form_class = ItemEstoqueForm
    template_name = 'sigad_app/registrar_item.html'
    success_url = reverse_lazy('item_estoque_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['editando'] = True
        return ctx


class ItemEstoqueDelete(LoginRequiredMixin, DeleteView):
    model = ItemEstoque
    template_name = 'sigad_app/form.html'
    success_url = reverse_lazy('item_estoque_list')
    extra_context = {'titulo': 'Excluir Item de Estoque', 'botao': 'Confirmar exclusão'}


class ItemEstoqueDetail(LoginRequiredMixin, DetailView):
    model = ItemEstoque
    template_name = 'sigad_app/item_estoque_detail.html'
    context_object_name = 'item_estoque'


# ─── Distribuição ─────────────────────────────────────────────────────────────

@login_required
def registrar_distribuicao(request):
    beneficiados_opts = Beneficiado.objects.order_by('nome')
    itens_qs = ItemEstoque.objects.filter(quantidade__gt=0).order_by('nome')
    itens_opts = [
        {'id': i.pk, 'label': f'{i.nome} — {i.quantidade} {i.unidade}', 'unidade': i.unidade}
        for i in itens_qs
    ]
    form_novo = BeneficiadoForm()
    selected_beneficiado_id = request.GET.get('beneficiado_id', '')

    if request.method == 'POST':
        action = request.POST.get('action', '')

        if action == 'novo_beneficiado':
            form_novo = BeneficiadoForm(request.POST)
            if form_novo.is_valid():
                novo = form_novo.save()
                messages.success(request, f'Beneficiado "{novo.nome}" cadastrado.')
                return redirect(f'{reverse_lazy("registrar_distribuicao")}?beneficiado_id={novo.pk}')

        else:
            beneficiado_id = request.POST.get('beneficiado_id', '').strip()
            try:
                linhas = json.loads(request.POST.get('linhas_json', '[]'))
            except (ValueError, TypeError):
                linhas = []

            erros = []
            if not beneficiado_id:
                erros.append('Selecione um beneficiado.')
            if not linhas:
                erros.append('Adicione pelo menos um item à distribuição.')

            if erros:
                for e in erros:
                    messages.error(request, e)
            else:
                try:
                    with transaction.atomic():
                        beneficiado = get_object_or_404(Beneficiado, pk=beneficiado_id)
                        dist = Distribuicao.objects.create(beneficiado=beneficiado)

                        for linha in linhas:
                            item = get_object_or_404(ItemEstoque, pk=linha['item_id'])
                            qtd = int(linha['quantidade'])
                            if qtd <= 0:
                                raise ValueError(f'Quantidade inválida para {item.nome}.')
                            if item.quantidade < qtd:
                                raise ValueError(
                                    f'Estoque insuficiente para "{item.nome}" '
                                    f'({item.quantidade} {item.unidade} disponível).'
                                )
                            LinhaDistribuicao.objects.create(
                                distribuicao=dist,
                                item_estoque=item,
                                quantidade=qtd,
                            )
                            item.quantidade -= qtd
                            item.save(update_fields=['quantidade'])

                        beneficiado.ultima_distribuicao = timezone.now().date()
                        beneficiado.save(update_fields=['ultima_distribuicao'])

                        messages.success(request, f'Distribuição #{dist.pk} registrada com sucesso.')
                        return redirect('distribuicao_detail', pk=dist.pk)

                except ValueError as exc:
                    messages.error(request, str(exc))

    return render(request, 'sigad_app/registrar_distribuicao.html', {
        'beneficiados_opts': beneficiados_opts,
        'itens_opts': itens_opts,
        'itens_opts_json': json.dumps(itens_opts),
        'form_novo': form_novo,
        'selected_beneficiado_id': selected_beneficiado_id,
    })


class DistribuicaoList(LoginRequiredMixin, ListView):
    model = Distribuicao
    template_name = 'sigad_app/distribuicao_list.html'
    context_object_name = 'distribuicoes'
    queryset = Distribuicao.objects.select_related('beneficiado')


class DistribuicaoDetail(LoginRequiredMixin, DetailView):
    model = Distribuicao
    template_name = 'sigad_app/distribuicao_detail.html'
    context_object_name = 'distribuicao'


class DistribuicaoUpdate(LoginRequiredMixin, UpdateView):
    model = Distribuicao
    fields = ['beneficiado']
    template_name = 'sigad_app/form.html'
    success_url = reverse_lazy('distribuicao_list')
    extra_context = {'titulo': 'Editar Distribuição', 'botao': 'Atualizar'}


class DistribuicaoDelete(LoginRequiredMixin, DeleteView):
    model = Distribuicao
    template_name = 'sigad_app/form.html'
    success_url = reverse_lazy('distribuicao_list')
    extra_context = {'titulo': 'Excluir Distribuição', 'botao': 'Confirmar exclusão'}


class LinhaDistribuicaoList(LoginRequiredMixin, ListView):
    model = LinhaDistribuicao
    template_name = 'sigad_app/linha_distribuicao_list.html'
    context_object_name = 'linhas_distribuicao'
    queryset = LinhaDistribuicao.objects.select_related(
        'distribuicao__beneficiado', 'item_estoque'
    )


class LinhaDistribuicaoDetail(LoginRequiredMixin, DetailView):
    model = LinhaDistribuicao
    template_name = 'sigad_app/linha_distribuicao_detail.html'
    context_object_name = 'linha_distribuicao'


# ─── Relatórios ───────────────────────────────────────────────────────────────

def _semana_corrente():
    """Retorna (inicio, fim) da semana corrente (seg–dom)."""
    hoje = timezone.localdate()
    inicio = hoje - timedelta(days=hoje.weekday())
    fim = inicio + timedelta(days=6)
    return inicio, fim


def _mes_corrente():
    """Retorna (inicio, fim) do mês corrente."""
    hoje = timezone.localdate()
    inicio = hoje.replace(day=1)
    if hoje.month == 12:
        fim = hoje.replace(year=hoje.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        fim = hoje.replace(month=hoje.month + 1, day=1) - timedelta(days=1)
    return inicio, fim


@login_required
def relatorios(request):
    periodo = request.GET.get('periodo', 'semanal')
    exportar = request.GET.get('export', '') == 'xlsx'
    hoje = timezone.localdate()

    PERIODOS_VALIDOS = ('semanal', 'mensal', 'beneficiario', 'beneficiado', 'categoria')
    if periodo not in PERIODOS_VALIDOS:
        periodo = 'semanal'

    labels = []
    values = []
    resumo_cards = []
    chart_type = 'bar'
    chart_index_axis = 'x'
    value_label = 'unidades'
    chart_title = ''
    chart_legend_hint = ''
    periodo_titulo = ''
    range_inicio = ''
    range_fim = ''
    col_ref = ''
    col_qtd = ''
    tipo_label = ''

    if periodo == 'semanal':
        inicio, fim = _semana_corrente()
        range_inicio = inicio.strftime('%d/%m/%Y')
        range_fim = fim.strftime('%d/%m/%Y')
        periodo_titulo = f'Semana {inicio.strftime("%d/%m")} – {fim.strftime("%d/%m/%Y")}'
        tipo_label = 'Semanal — unidades distribuídas por dia'

        nomes_dias = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
        contagem = {i: 0 for i in range(7)}
        linhas_qs = (
            LinhaDistribuicao.objects
            .filter(distribuicao__registrado_em__date__range=(inicio, fim))
            .select_related('distribuicao')
        )
        for linha in linhas_qs:
            dia_semana = linha.distribuicao.registrado_em.weekday()
            contagem[dia_semana] += linha.quantidade

        labels = nomes_dias
        values = [contagem[i] for i in range(7)]

        total_dist = Distribuicao.objects.filter(registrado_em__date__range=(inicio, fim)).count()
        total_unid = sum(values)
        benef_atend = (
            Distribuicao.objects
            .filter(registrado_em__date__range=(inicio, fim))
            .values('beneficiado').distinct().count()
        )
        resumo_cards = [
            {'title': 'Distribuições', 'value': total_dist, 'delta': 'na semana', 'icon': 'arrow-right-left', 'tone': 'tone-blue'},
            {'title': 'Unidades', 'value': total_unid, 'delta': 'distribuídas', 'icon': 'boxes', 'tone': 'tone-green'},
            {'title': 'Beneficiados', 'value': benef_atend, 'delta': 'atendidos', 'icon': 'heart-handshake', 'tone': 'tone-purple'},
        ]
        chart_type = 'bar'
        chart_index_axis = 'x'
        chart_title = 'Unidades distribuídas por dia da semana'
        chart_legend_hint = 'Semana corrente (seg–dom)'
        value_label = 'unidades'
        col_ref = 'Dia'
        col_qtd = 'Unidades distribuídas'

    elif periodo == 'mensal':
        inicio, fim = _mes_corrente()
        range_inicio = inicio.strftime('%d/%m/%Y')
        range_fim = fim.strftime('%d/%m/%Y')
        periodo_titulo = inicio.strftime('%B de %Y').capitalize()
        tipo_label = 'Mensal — unidades distribuídas por semana'

        # Agrupar por semana do mês
        semanas = {}
        d = inicio
        semana_num = 1
        while d <= fim:
            chave = f'Semana {semana_num}'
            semanas[chave] = 0
            d_fim_sem = min(d + timedelta(days=6), fim)
            linhas_qs = LinhaDistribuicao.objects.filter(
                distribuicao__registrado_em__date__range=(d, d_fim_sem)
            )
            semanas[chave] = sum(l.quantidade for l in linhas_qs)
            d = d_fim_sem + timedelta(days=1)
            semana_num += 1

        labels = list(semanas.keys())
        values = list(semanas.values())

        total_dist = Distribuicao.objects.filter(registrado_em__date__range=(inicio, fim)).count()
        total_unid = sum(values)
        benef_atend = (
            Distribuicao.objects
            .filter(registrado_em__date__range=(inicio, fim))
            .values('beneficiado').distinct().count()
        )
        resumo_cards = [
            {'title': 'Distribuições', 'value': total_dist, 'delta': 'no mês', 'icon': 'arrow-right-left', 'tone': 'tone-blue'},
            {'title': 'Unidades', 'value': total_unid, 'delta': 'distribuídas', 'icon': 'boxes', 'tone': 'tone-green'},
            {'title': 'Beneficiados', 'value': benef_atend, 'delta': 'atendidos', 'icon': 'heart-handshake', 'tone': 'tone-purple'},
        ]
        chart_type = 'bar'
        chart_index_axis = 'x'
        chart_title = 'Unidades distribuídas por semana do mês'
        chart_legend_hint = periodo_titulo
        value_label = 'unidades'
        col_ref = 'Semana'
        col_qtd = 'Unidades distribuídas'

    elif periodo == 'beneficiario':
        inicio, fim = _mes_corrente()
        range_inicio = inicio.strftime('%d/%m/%Y')
        range_fim = fim.strftime('%d/%m/%Y')
        periodo_titulo = f'Doações por beneficiário — {inicio.strftime("%B/%Y").capitalize()}'
        tipo_label = 'Por beneficiário (quem doou) — top 10 do mês'

        qs = (
            ItemEstoque.objects
            .filter(beneficiario__isnull=False, criado_em__date__range=(inicio, fim))
            .values('beneficiario__nome')
            .annotate(total=Sum('quantidade_doada'))
            .order_by('-total')[:10]
        )
        labels = [r['beneficiario__nome'] for r in qs]
        values = [r['total'] for r in qs]

        total_benef = len(labels)
        total_unid = sum(values)
        resumo_cards = [
            {'title': 'Beneficiários', 'value': total_benef, 'delta': 'com doação no mês', 'icon': 'users', 'tone': 'tone-green'},
            {'title': 'Unidades doadas', 'value': total_unid, 'delta': 'no mês', 'icon': 'boxes', 'tone': 'tone-blue'},
        ]
        chart_type = 'bar'
        chart_index_axis = 'y'
        chart_title = 'Top beneficiários por unidades doadas (mês corrente)'
        chart_legend_hint = 'Quem doou itens ao estoque'
        value_label = 'unidades'
        col_ref = 'Beneficiário'
        col_qtd = 'Unidades doadas'

    elif periodo == 'beneficiado':
        inicio, fim = _mes_corrente()
        range_inicio = inicio.strftime('%d/%m/%Y')
        range_fim = fim.strftime('%d/%m/%Y')
        periodo_titulo = f'Distribuições por beneficiado — {inicio.strftime("%B/%Y").capitalize()}'
        tipo_label = 'Por beneficiado (quem recebeu) — top 10 do mês'

        qs = (
            LinhaDistribuicao.objects
            .filter(distribuicao__registrado_em__date__range=(inicio, fim))
            .values('distribuicao__beneficiado__nome')
            .annotate(total=Sum('quantidade'))
            .order_by('-total')[:10]
        )
        labels = [r['distribuicao__beneficiado__nome'] for r in qs]
        values = [r['total'] for r in qs]

        total_benef = len(labels)
        total_unid = sum(values)
        total_dist = (
            Distribuicao.objects
            .filter(registrado_em__date__range=(inicio, fim))
            .count()
        )
        resumo_cards = [
            {'title': 'Beneficiados', 'value': total_benef, 'delta': 'atendidos no mês', 'icon': 'heart-handshake', 'tone': 'tone-purple'},
            {'title': 'Unidades recebidas', 'value': total_unid, 'delta': 'no mês', 'icon': 'boxes', 'tone': 'tone-blue'},
            {'title': 'Distribuições', 'value': total_dist, 'delta': 'no mês', 'icon': 'arrow-right-left', 'tone': 'tone-green'},
        ]
        chart_type = 'bar'
        chart_index_axis = 'y'
        chart_title = 'Top beneficiados por unidades recebidas (mês corrente)'
        chart_legend_hint = 'Quem recebeu itens nas distribuições'
        value_label = 'unidades'
        col_ref = 'Beneficiado'
        col_qtd = 'Unidades recebidas'

    elif periodo == 'categoria':
        inicio, fim = _mes_corrente()
        range_inicio = inicio.strftime('%d/%m/%Y')
        range_fim = fim.strftime('%d/%m/%Y')
        periodo_titulo = f'Distribuições por categoria — {inicio.strftime("%B/%Y").capitalize()}'
        tipo_label = 'Por categoria de item — mês corrente'

        qs = (
            LinhaDistribuicao.objects
            .filter(distribuicao__registrado_em__date__range=(inicio, fim))
            .values('item_estoque__categoria')
            .annotate(total=Sum('quantidade'))
            .order_by('-total')
        )
        labels = [r['item_estoque__categoria'] for r in qs]
        values = [r['total'] for r in qs]

        top_cat = labels[0] if labels else '—'
        total_unid = sum(values)
        resumo_cards = [
            {'title': 'Categoria líder', 'value': top_cat, 'delta': 'maior volume', 'icon': 'tag', 'tone': 'tone-orange'},
            {'title': 'Unidades', 'value': total_unid, 'delta': 'distribuídas no mês', 'icon': 'boxes', 'tone': 'tone-blue'},
            {'title': 'Categorias', 'value': len(labels), 'delta': 'com distribuição', 'icon': 'list', 'tone': 'tone-green'},
        ]
        chart_type = 'bar'
        chart_index_axis = 'y'
        chart_title = 'Unidades distribuídas por categoria (mês corrente)'
        chart_legend_hint = 'Categorias com distribuição no período'
        value_label = 'unidades'
        col_ref = 'Categoria'
        col_qtd = 'Unidades distribuídas'

    if exportar:
        buf = build_relatorio_distribuicao_xlsx(
            periodo_titulo=periodo_titulo,
            tipo_label=tipo_label,
            col_ref=col_ref,
            col_qtd=col_qtd,
            labels=labels,
            values=values,
            total=sum(values),
        )
        filename = f'sigad-relatorio-{periodo}-{hoje.strftime("%Y%m%d")}.xlsx'
        response = HttpResponse(
            buf.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    return render(request, 'sigad_app/relatorios.html', {
        'periodo': periodo,
        'periodo_titulo': periodo_titulo,
        'range_inicio': range_inicio,
        'range_fim': range_fim,
        'today': hoje.strftime('%d/%m/%Y'),
        'resumo_cards': resumo_cards,
        'chart_title': chart_title,
        'chart_legend_hint': chart_legend_hint,
        'chart_type': chart_type,
        'chart_index_axis': chart_index_axis,
        'value_label': value_label,
        'chart_labels_json': json.dumps(labels, ensure_ascii=False),
        'chart_values_json': json.dumps(values),
        'has_data': bool(labels),
    })
