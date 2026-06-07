from django import forms

from sigad_app.models import Beneficiario, ItemEstoque


class ItemEstoqueForm(forms.ModelForm):
    class Meta:
        model = ItemEstoque
        fields = [
            'categoria',
            'nome',
            'quantidade',
            'unidade',
            'validade',
            'doador',
            'observacoes',
        ]
        labels = {
            'categoria': 'Categoria',
            'nome': 'Nome do item',
            'quantidade': 'Quantidade',
            'unidade': 'Unidade',
            'validade': 'Data de validade',
            'doador': 'Nome do doador',
            'observacoes': 'Observações',
        }
        widgets = {
            'categoria': forms.Select(attrs={'class': 'form-select sigad-input', 'required': True}),
            'nome': forms.TextInput(attrs={'class': 'form-control sigad-input', 'placeholder': 'Ex: Arroz branco', 'required': True}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control sigad-input', 'min': 1, 'required': True}),
            'unidade': forms.Select(attrs={'class': 'form-select sigad-input', 'required': True}),
            'validade': forms.DateInput(attrs={'class': 'form-control sigad-input', 'type': 'date'}),
            'doador': forms.TextInput(attrs={'class': 'form-control sigad-input', 'placeholder': 'Nome do doador'}),
            'observacoes': forms.Textarea(
                attrs={'class': 'form-control sigad-input', 'rows': 5, 'placeholder': 'Informações adicionais...'}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['categoria'].choices = [('', 'Selecione…')] + list(ItemEstoque.CATEGORIAS)
        self.fields['unidade'].widget = forms.Select(
            choices=[
                ('', 'Selecione'),
                ('pacote', 'pacote'),
                ('unidade', 'unidade'),
                ('litro', 'litro'),
                ('kg', 'kg'),
            ],
            attrs={'class': 'form-select sigad-input', 'required': True},
        )
        self.fields['validade'].required = False
        self.fields['doador'].required = False
        self.fields['observacoes'].required = False

    def clean_categoria(self):
        v = self.cleaned_data.get('categoria')
        if not v:
            raise forms.ValidationError('Selecione uma categoria.')
        return v


class BeneficiarioForm(forms.ModelForm):
    class Meta:
        model = Beneficiario
        fields = ['nome', 'cpf', 'telefone', 'email', 'endereco']
        labels = {
            'nome': 'Nome completo',
            'cpf': 'CPF',
            'telefone': 'Telefone',
            'email': 'E-mail',
            'endereco': 'Endereço',
        }
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control sigad-input', 'required': True}),
            'cpf': forms.TextInput(attrs={'class': 'form-control sigad-input', 'placeholder': '000.000.000-00', 'required': True}),
            'telefone': forms.TextInput(attrs={'class': 'form-control sigad-input', 'required': True}),
            'email': forms.EmailInput(attrs={'class': 'form-control sigad-input', 'required': True}),
            'endereco': forms.TextInput(attrs={'class': 'form-control sigad-input', 'required': True}),
        }
