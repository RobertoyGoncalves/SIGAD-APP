import json
from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeDoneView, PasswordChangeView
from django.db import transaction
from django.db.models import Q, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)

from sigad_app.forms import BeneficiadoForm, CadastroUsuarioForm, DoadorForm, ItemEstoqueForm
from sigad_app.models import (
    Beneficiado,
    Distribuicao,
    Doador,
    ItemEstoque,
    LinhaDistribuicao,
)
from sigad_app.report_export import build_relatorio_distribuicao_xlsx


# ─── Páginas públicas ─────────────────────────────────────────────────────────

class Landing(TemplateView):
    template_name = 'sigad_app/landing.html'


# ─── Autenticação ─────────────────────────────────────────────────────────

class SigadLoginView(LoginView):
    template_name = 'sigad_app/form.html'
    redirect_authenticated_user = True
    extra_context = {'titulo': 'Entrar no SIGAD', 'botao': 'Entrar'}


class SigadLogoutView(LogoutView):
    next_page = 'landing'


class SigadPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'sigad_app/form.html'
    success_url = reverse_lazy('password_change_done')
    extra_context = {'titulo': 'Alterar senha', 'botao': 'Salvar nova senha'}


class SigadPasswordChangeDoneView(LoginRequiredMixin, PasswordChangeDoneView):
    template_name = 'sigad_app/password_change_done.html'


class CadastroUsuarioView(CreateView):
    form_class = CadastroUsuarioForm
    template_name = 'sigad_app/form.html'
    success_url = reverse_lazy('login')
    extra_context = {'titulo': 'Criar conta', 'botao': 'Cadastrar'}

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Conta criada com sucesso! Faça login para continuar.')
        return response


# ─── Gerenciamento de usuários (superuser) ───────────────────────────────────

class SuperuserRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        messages.error(self.request, 'Você não tem permissão para acessar essa área.')
        return redirect('dashboard')


class UsuarioListView(SuperuserRequiredMixin, ListView):
    model = User
    template_name = 'sigad_app/usuario_list.html'
    context_object_name = 'usuarios'
    ordering = ['username']


@user_passes_test(lambda u: u.is_superuser)
@require_POST
def alternar_admin(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    if usuario == request.user:
        messages.error(request, 'Você não pode alterar suas próprias permissões.')
        return redirect('usuario_list')
    usuario.is_staff = not usuario.is_staff
    usuario.is_superuser = not usuario.is_superuser
    usuario.save()
    messages.success(request, f'Permissões de {usuario.username} atualizadas.')
    return redirect('usuario_list')


@user_passes_test(lambda u: u.is_superuser)
@require_POST
def alternar_ativo(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    if usuario == request.user:
        messages.error(request, 'Você não pode desativar sua própria conta.')
        return redirect('usuario_list')
    usuario.is_active = not usuario.is_active
    usuario.save()
    messages.success(request, f'Conta de {usuario.username} {"ativada" if usuario.is_active else "desativada"}.')
    return redirect('usuario_list')


# ─── Dashboard ───────────────────────────────────────────────────────────────

class Dashboard(LoginRequiredMixin, TemplateView):
    template_name = 'sigad_app/dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        itens_qs = ItemEstoque.objects
        doadores_qs = Doador.objects
        beneficiados_qs = Beneficiado.objects
        distribuicoes_qs = Distribuicao.objects
        if not user.is_superuser:
            itens_qs = itens_qs.filter(usuario=user)
            doadores_qs = doadores_qs.filter(usuario=user)
            beneficiados_qs = beneficiados_qs.filter(usuario=user)
            distribuicoes_qs = distribuicoes_qs.filter(usuario=user)
        ctx['cards'] = [
            {
                'title': 'Itens no Estoque',
                'value': itens_qs.count(),
                'delta': 'Total de itens cadastrados',
                'icon': 'box-seam',
                'tone': 'tone-blue',
            },
            {
                'title': 'Doadores',
                'value': doadores_qs.count(),
                'delta': 'Quem doa',
                'icon': 'users',
                'tone': 'tone-green',
            },
            {
                'title': 'Beneficiados',
                'value': beneficiados_qs.count(),
                'delta': 'Quem recebe',
                'icon': 'heart-handshake',
                'tone': 'tone-purple',
            },
            {
                'title': 'Distribuições',
                'value': distribuicoes_qs.count(),
                'delta': 'Total registrado',
                'icon': 'arrow-right-left',
                'tone': 'tone-orange',
            },
        ]
        atividades = []
        for d in distribuicoes_qs.select_related('beneficiado').order_by('-registrado_em')[:5]:
            atividades.append({
                'titulo': f'Distribuição #{d.pk}',
                'descricao': f'Para {d.beneficiado.nome}',
                'tempo': d.registrado_em.strftime('%d/%m/%Y %H:%M'),
            })
        for i in itens_qs.select_related('doador').order_by('-criado_em')[:5]:
            desc = f'{i.quantidade} {i.unidade}'
            if i.doador:
                desc += f' — {i.doador.nome}'
            atividades.append({
                'titulo': f'Doação recebida: {i.nome}',
                'descricao': desc,
                'tempo': i.criado_em.strftime('%d/%m/%Y %H:%M'),
            })
        atividades.sort(key=lambda x: x['tempo'], reverse=True)
        ctx['atividades'] = atividades[:8]
        return ctx


# ─── Doador (quem DOA) ───────────────────────────────────────────────────────

@login_required
def doador_list(request):
    q = request.GET.get('q', '').strip()
    if request.user.is_superuser:
        qs = Doador.objects.prefetch_related('itens_doados').all()
    else:
        qs = Doador.objects.prefetch_related('itens_doados').filter(usuario=request.user)
    if q:
        qs = qs.filter(nome__icontains=q)

    if request.method == 'POST':
        form = DoadorForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.usuario = request.user
            obj.save()
            messages.success(request, 'Doador cadastrado com sucesso.')
            return redirect('doador_list')
    else:
        form = DoadorForm()

    doadores_data = []
    for doador in qs:
        itens = list(doador.itens_doados.order_by('-criado_em'))
        doadores_data.append({
            'obj': doador,
            'itens': itens,
            'total_doacoes': len(itens),
            'total_unidades': sum(i.quantidade for i in itens),
        })

    return render(request, 'sigad_app/doador_list.html', {
        'doadores_data': doadores_data,
        'filtro_q': q,
        'form': form,
    })


class DoadorUpdate(LoginRequiredMixin, UpdateView):
    model = Doador
    form_class = DoadorForm
    template_name = 'sigad_app/form.html'
    success_url = reverse_lazy('doador_list')
    extra_context = {'titulo': 'Editar Doador', 'botao': 'Atualizar'}

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_superuser:
            return qs
        return qs.filter(usuario=self.request.user)


class DoadorDelete(LoginRequiredMixin, DeleteView):
    model = Doador
    template_name = 'sigad_app/form.html'
    success_url = reverse_lazy('doador_list')
    extra_context = {'titulo': 'Excluir Doador', 'botao': 'Confirmar exclusão'}

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_superuser:
            return qs
        return qs.filter(usuario=self.request.user)


# ─── Beneficiado (quem RECEBE) ────────────────────────────────────────────────

class BeneficiadoCreate(LoginRequiredMixin, CreateView):
    model = Beneficiado
    form_class = BeneficiadoForm
    template_name = 'sigad_app/form.html'
    success_url = reverse_lazy('beneficiado_list')
    extra_context = {'titulo': 'Cadastrar Beneficiado', 'botao': 'Salvar'}

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        messages.success(self.request, 'Beneficiado cadastrado com sucesso.')
        return super().form_valid(form)


class BeneficiadoList(LoginRequiredMixin, ListView):
    model = Beneficiado
    template_name = 'sigad_app/beneficiado_list.html'
    context_object_name = 'beneficiados'

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_superuser:
            qs = qs.filter(usuario=self.request.user)
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

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_superuser:
            return qs
        return qs.filter(usuario=self.request.user)


class BeneficiadoUpdate(LoginRequiredMixin, UpdateView):
    model = Beneficiado
    form_class = BeneficiadoForm
    template_name = 'sigad_app/form.html'
    success_url = reverse_lazy('beneficiado_list')
    extra_context = {'titulo': 'Editar Beneficiado', 'botao': 'Atualizar'}

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_superuser:
            return qs
        return qs.filter(usuario=self.request.user)


class BeneficiadoDelete(LoginRequiredMixin, DeleteView):
    model = Beneficiado
    template_name = 'sigad_app/form.html'
    success_url = reverse_lazy('beneficiado_list')
    extra_context = {'titulo': 'Excluir Beneficiado', 'botao': 'Confirmar exclusão'}

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_superuser:
            return qs
        return qs.filter(usuario=self.request.user)


# ─── Estoque ──────────────────────────────────────────────────────────────────

@login_required
def registrar_item(request):
    if request.method == 'POST':
        form = ItemEstoqueForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.quantidade_doada = item.quantidade
            item.usuario = request.user
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
    if request.user.is_superuser:
        qs = ItemEstoque.objects.select_related('doador').all()
    else:
        qs = ItemEstoque.objects.select_related('doador').filter(usuario=request.user)
    if q:
        qs = qs.filter(
            Q(nome__icontains=q) | Q(doador__nome__icontains=q)
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

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_superuser:
            qs = qs.filter(usuario=self.request.user)
        return qs.select_related('doador')


class ItemEstoqueUpdate(LoginRequiredMixin, UpdateView):
    model = ItemEstoque
    form_class = ItemEstoqueForm
    template_name = 'sigad_app/registrar_item.html'
    success_url = reverse_lazy('item_estoque_list')

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_superuser:
            return qs
        return qs.filter(usuario=self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['editando'] = True
        return ctx


class ItemEstoqueDelete(LoginRequiredMixin, DeleteView):
    model = ItemEstoque
    template_name = 'sigad_app/form.html'
    success_url = reverse_lazy('item_estoque_list')
    extra_context = {'titulo': 'Excluir Item de Estoque', 'botao': 'Confirmar exclusão'}

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_superuser:
            return qs
        return qs.filter(usuario=self.request.user)


class ItemEstoqueDetail(LoginRequiredMixin, DetailView):
    model = ItemEstoque
    template_name = 'sigad_app/item_estoque_detail.html'
    context_object_name = 'item_estoque'

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_superuser:
            return qs
        return qs.filter(usuario=self.request.user)


# ─── Distribuição ─────────────────────────────────────────────────────────────

@login_required
def registrar_distribuicao(request):
    if request.user.is_superuser:
        beneficiados_opts = Beneficiado.objects.order_by('nome')
        itens_qs = ItemEstoque.objects.filter(quantidade__gt=0).order_by('nome')
    else:
        beneficiados_opts = Beneficiado.objects.filter(usuario=request.user).order_by('nome')
        itens_qs = ItemEstoque.objects.filter(usuario=request.user, quantidade__gt=0).order_by('nome')
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
                novo = form_novo.save(commit=False)
                novo.usuario = request.user
                novo.save()
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
                        if request.user.is_superuser:
                            beneficiado = get_object_or_404(Beneficiado, pk=beneficiado_id)
                            dist = Distribuicao.objects.create(beneficiado=beneficiado, usuario=request.user)
                        else:
                            beneficiado = get_object_or_404(Beneficiado, pk=beneficiado_id, usuario=request.user)
                            dist = Distribuicao.objects.create(beneficiado=beneficiado, usuario=request.user)

                        for linha in linhas:
                            if request.user.is_superuser:
                                item = get_object_or_404(ItemEstoque, pk=linha['item_id'])
                            else:
                                item = get_object_or_404(ItemEstoque, pk=linha['item_id'], usuario=request.user)
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

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_superuser:
            qs = qs.filter(usuario=self.request.user)
        return qs.select_related('beneficiado')


class DistribuicaoDetail(LoginRequiredMixin, DetailView):
    model = Distribuicao
    template_name = 'sigad_app/distribuicao_detail.html'
    context_object_name = 'distribuicao'

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_superuser:
            return qs
        return qs.filter(usuario=self.request.user)


class DistribuicaoUpdate(LoginRequiredMixin, UpdateView):
    model = Distribuicao
    fields = ['beneficiado']
    template_name = 'sigad_app/form.html'
    success_url = reverse_lazy('distribuicao_list')
    extra_context = {'titulo': 'Editar Distribuição', 'botao': 'Atualizar'}

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_superuser:
            return qs
        return qs.filter(usuario=self.request.user)


class DistribuicaoDelete(LoginRequiredMixin, DeleteView):
    model = Distribuicao
    template_name = 'sigad_app/form.html'
    success_url = reverse_lazy('distribuicao_list')
    extra_context = {'titulo': 'Excluir Distribuição', 'botao': 'Confirmar exclusão'}

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_superuser:
            return qs
        return qs.filter(usuario=self.request.user)


class LinhaDistribuicaoList(LoginRequiredMixin, ListView):
    model = LinhaDistribuicao
    template_name = 'sigad_app/linha_distribuicao_list.html'
    context_object_name = 'linhas_distribuicao'

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_superuser:
            qs = qs.filter(distribuicao__usuario=self.request.user)
        return qs.select_related(
            'distribuicao__beneficiado', 'item_estoque'
        )


class LinhaDistribuicaoDetail(LoginRequiredMixin, DetailView):
    model = LinhaDistribuicao
    template_name = 'sigad_app/linha_distribuicao_detail.html'
    context_object_name = 'linha_distribuicao'

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_superuser:
            return qs
        return qs.filter(distribuicao__usuario=self.request.user)


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

    PERIODOS_VALIDOS = ('semanal', 'mensal', 'doador', 'beneficiado', 'categoria')
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

    user = request.user
    filtro_dist = {} if user.is_superuser else {'usuario': user}
    filtro_linha_dist = {} if user.is_superuser else {'distribuicao__usuario': user}
    filtro_item = {} if user.is_superuser else {'usuario': user}

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
            .filter(
                distribuicao__registrado_em__date__range=(inicio, fim),
                **filtro_linha_dist,
            )
            .select_related('distribuicao')
        )
        for linha in linhas_qs:
            dia_semana = linha.distribuicao.registrado_em.weekday()
            contagem[dia_semana] += linha.quantidade

        labels = nomes_dias
        values = [contagem[i] for i in range(7)]

        total_dist = Distribuicao.objects.filter(
            registrado_em__date__range=(inicio, fim),
            **filtro_dist,
        ).count()
        total_unid = sum(values)
        benef_atend = (
            Distribuicao.objects
            .filter(registrado_em__date__range=(inicio, fim), **filtro_dist)
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
                distribuicao__registrado_em__date__range=(d, d_fim_sem),
                **filtro_linha_dist,
            )
            semanas[chave] = sum(l.quantidade for l in linhas_qs)
            d = d_fim_sem + timedelta(days=1)
            semana_num += 1

        labels = list(semanas.keys())
        values = list(semanas.values())

        total_dist = Distribuicao.objects.filter(
            registrado_em__date__range=(inicio, fim),
            **filtro_dist,
        ).count()
        total_unid = sum(values)
        benef_atend = (
            Distribuicao.objects
            .filter(registrado_em__date__range=(inicio, fim), **filtro_dist)
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

    elif periodo == 'doador':
        inicio, fim = _mes_corrente()
        range_inicio = inicio.strftime('%d/%m/%Y')
        range_fim = fim.strftime('%d/%m/%Y')
        periodo_titulo = f'Doações por doador — {inicio.strftime("%B/%Y").capitalize()}'
        tipo_label = 'Por doador (quem doou) — top 10 do mês'

        qs = (
            ItemEstoque.objects
            .filter(
                doador__isnull=False,
                criado_em__date__range=(inicio, fim),
                **filtro_item,
            )
            .values('doador__nome')
            .annotate(total=Sum('quantidade_doada'))
            .order_by('-total')[:10]
        )
        labels = [r['doador__nome'] for r in qs]
        values = [r['total'] for r in qs]

        total_benef = len(labels)
        total_unid = sum(values)
        resumo_cards = [
            {'title': 'Doadores', 'value': total_benef, 'delta': 'com doação no mês', 'icon': 'users', 'tone': 'tone-green'},
            {'title': 'Unidades doadas', 'value': total_unid, 'delta': 'no mês', 'icon': 'boxes', 'tone': 'tone-blue'},
        ]
        chart_type = 'bar'
        chart_index_axis = 'y'
        chart_title = 'Top doadores por unidades doadas (mês corrente)'
        chart_legend_hint = 'Quem doou itens ao estoque'
        value_label = 'unidades'
        col_ref = 'Doador'
        col_qtd = 'Unidades doadas'

    elif periodo == 'beneficiado':
        inicio, fim = _mes_corrente()
        range_inicio = inicio.strftime('%d/%m/%Y')
        range_fim = fim.strftime('%d/%m/%Y')
        periodo_titulo = f'Distribuições por beneficiado — {inicio.strftime("%B/%Y").capitalize()}'
        tipo_label = 'Por beneficiado (quem recebeu) — top 10 do mês'

        qs = (
            LinhaDistribuicao.objects
            .filter(
                distribuicao__registrado_em__date__range=(inicio, fim),
                **filtro_linha_dist,
            )
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
            .filter(registrado_em__date__range=(inicio, fim), **filtro_dist)
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
            .filter(
                distribuicao__registrado_em__date__range=(inicio, fim),
                **filtro_linha_dist,
            )
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
