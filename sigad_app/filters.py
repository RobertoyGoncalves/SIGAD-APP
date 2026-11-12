import django_filters
from django import forms

from sigad_app.models import ItemEstoque


class ItemEstoqueFilter(django_filters.FilterSet):
    nome = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Nome',
        widget=forms.TextInput(attrs={'placeholder': 'Buscar por nome…', 'class': 'form-control'}),
    )
    categoria = django_filters.ChoiceFilter(
        choices=[('', 'Todas as categorias')] + ItemEstoque.CATEGORIAS,
        label='Categoria',
        empty_label=None,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    class Meta:
        model = ItemEstoque
        fields = ['nome', 'categoria']
