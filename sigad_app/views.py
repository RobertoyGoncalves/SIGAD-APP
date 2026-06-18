from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)

from sigad_app.models import Beneficiario, Distribuicao, ItemEstoque, LinhaDistribuicao


class Landing(TemplateView):
    template_name = 'sigad_app/landing.html'


class Dashboard(LoginRequiredMixin, TemplateView):
    template_name = 'sigad_app/dashboard.html'


class BeneficiarioCreate(LoginRequiredMixin, CreateView):
    model = Beneficiario
    fields = ['nome', 'cpf', 'telefone', 'email', 'endereco']
    template_name = 'sigad_app/form.html'
    success_url = reverse_lazy('beneficiario_list')
    extra_context = {
        'titulo': 'Cadastrar Beneficiário',
        'botao': 'Salvar',
    }


class BeneficiarioUpdate(LoginRequiredMixin, UpdateView):
    model = Beneficiario
    fields = ['nome', 'cpf', 'telefone', 'email', 'endereco']
    template_name = 'sigad_app/form.html'
    success_url = reverse_lazy('beneficiario_list')
    extra_context = {
        'titulo': 'Editar Beneficiário',
        'botao': 'Atualizar',
    }


class BeneficiarioDelete(LoginRequiredMixin, DeleteView):
    model = Beneficiario
    template_name = 'sigad_app/form.html'
    success_url = reverse_lazy('beneficiario_list')
    extra_context = {
        'titulo': 'Excluir Beneficiário',
        'botao': 'Confirmar exclusão',
    }


class BeneficiarioList(LoginRequiredMixin, ListView):
    model = Beneficiario
    template_name = 'sigad_app/beneficiario_list.html'
    context_object_name = 'beneficiarios'


class BeneficiarioDetail(LoginRequiredMixin, DetailView):
    model = Beneficiario
    template_name = 'sigad_app/beneficiario_detail.html'
    context_object_name = 'beneficiario'


class ItemEstoqueCreate(LoginRequiredMixin, CreateView):
    model = ItemEstoque
    fields = [
        'nome',
        'categoria',
        'quantidade',
        'unidade',
        'validade',
        'doador',
        'observacoes',
    ]
    template_name = 'sigad_app/form.html'
    success_url = reverse_lazy('item_estoque_list')
    extra_context = {
        'titulo': 'Cadastrar Item de Estoque',
        'botao': 'Salvar',
    }


class ItemEstoqueUpdate(LoginRequiredMixin, UpdateView):
    model = ItemEstoque
    fields = [
        'nome',
        'categoria',
        'quantidade',
        'unidade',
        'validade',
        'doador',
        'observacoes',
    ]
    template_name = 'sigad_app/form.html'
    success_url = reverse_lazy('item_estoque_list')
    extra_context = {
        'titulo': 'Editar Item de Estoque',
        'botao': 'Atualizar',
    }


class ItemEstoqueDelete(LoginRequiredMixin, DeleteView):
    model = ItemEstoque
    template_name = 'sigad_app/form.html'
    success_url = reverse_lazy('item_estoque_list')
    extra_context = {
        'titulo': 'Excluir Item de Estoque',
        'botao': 'Confirmar exclusão',
    }


class ItemEstoqueList(LoginRequiredMixin, ListView):
    model = ItemEstoque
    template_name = 'sigad_app/item_estoque_list.html'
    context_object_name = 'itens_estoque'


class ItemEstoqueDetail(LoginRequiredMixin, DetailView):
    model = ItemEstoque
    template_name = 'sigad_app/item_estoque_detail.html'
    context_object_name = 'item_estoque'


class DistribuicaoCreate(LoginRequiredMixin, CreateView):
    model = Distribuicao
    fields = ['beneficiario']
    template_name = 'sigad_app/form.html'
    success_url = reverse_lazy('distribuicao_list')
    extra_context = {
        'titulo': 'Cadastrar Distribuição',
        'botao': 'Salvar',
    }


class DistribuicaoUpdate(LoginRequiredMixin, UpdateView):
    model = Distribuicao
    fields = ['beneficiario']
    template_name = 'sigad_app/form.html'
    success_url = reverse_lazy('distribuicao_list')
    extra_context = {
        'titulo': 'Editar Distribuição',
        'botao': 'Atualizar',
    }


class DistribuicaoDelete(LoginRequiredMixin, DeleteView):
    model = Distribuicao
    template_name = 'sigad_app/form.html'
    success_url = reverse_lazy('distribuicao_list')
    extra_context = {
        'titulo': 'Excluir Distribuição',
        'botao': 'Confirmar exclusão',
    }


class DistribuicaoList(LoginRequiredMixin, ListView):
    model = Distribuicao
    template_name = 'sigad_app/distribuicao_list.html'
    context_object_name = 'distribuicoes'


class DistribuicaoDetail(LoginRequiredMixin, DetailView):
    model = Distribuicao
    template_name = 'sigad_app/distribuicao_detail.html'
    context_object_name = 'distribuicao'


class LinhaDistribuicaoCreate(LoginRequiredMixin, CreateView):
    model = LinhaDistribuicao
    fields = ['distribuicao', 'item_estoque', 'quantidade']
    template_name = 'sigad_app/form.html'
    success_url = reverse_lazy('linha_distribuicao_list')
    extra_context = {
        'titulo': 'Cadastrar Linha de Distribuição',
        'botao': 'Salvar',
    }


class LinhaDistribuicaoUpdate(LoginRequiredMixin, UpdateView):
    model = LinhaDistribuicao
    fields = ['distribuicao', 'item_estoque', 'quantidade']
    template_name = 'sigad_app/form.html'
    success_url = reverse_lazy('linha_distribuicao_list')
    extra_context = {
        'titulo': 'Editar Linha de Distribuição',
        'botao': 'Atualizar',
    }


class LinhaDistribuicaoDelete(LoginRequiredMixin, DeleteView):
    model = LinhaDistribuicao
    template_name = 'sigad_app/form.html'
    success_url = reverse_lazy('linha_distribuicao_list')
    extra_context = {
        'titulo': 'Excluir Linha de Distribuição',
        'botao': 'Confirmar exclusão',
    }


class LinhaDistribuicaoList(LoginRequiredMixin, ListView):
    model = LinhaDistribuicao
    template_name = 'sigad_app/linha_distribuicao_list.html'
    context_object_name = 'linhas_distribuicao'


class LinhaDistribuicaoDetail(LoginRequiredMixin, DetailView):
    model = LinhaDistribuicao
    template_name = 'sigad_app/linha_distribuicao_detail.html'
    context_object_name = 'linha_distribuicao'
