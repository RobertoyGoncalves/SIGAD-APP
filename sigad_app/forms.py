from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from sigad_app.models import Beneficiado, Doador, ItemEstoque


class CadastroUsuarioForm(UserCreationForm):
    email = forms.EmailField(required=True, label='E-mail')

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control sigad-input'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class DoadorForm(forms.ModelForm):
    """Formulário para Doador — quem DOA itens ao estoque."""

    class Meta:
        model = Doador
        fields = ['nome', 'cpf', 'telefone', 'email', 'endereco', 'observacoes']
        labels = {
            'nome': 'Nome completo',
            'cpf': 'CPF',
            'telefone': 'Telefone',
            'email': 'E-mail',
            'endereco': 'Endereço',
            'observacoes': 'Observações',
        }
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control sigad-input', 'required': True}),
            'cpf': forms.TextInput(attrs={'class': 'form-control sigad-input', 'placeholder': '000.000.000-00'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control sigad-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-control sigad-input'}),
            'endereco': forms.TextInput(attrs={'class': 'form-control sigad-input'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control sigad-input', 'rows': 3, 'placeholder': 'Informações adicionais…'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in ['cpf', 'telefone', 'email', 'endereco', 'observacoes']:
            self.fields[f].required = False


class BeneficiadoForm(forms.ModelForm):
    """Formulário para Beneficiado — quem RECEBE itens na distribuição."""

    class Meta:
        model = Beneficiado
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
            'doador': 'Doador (quem doou)',
            'observacoes': 'Observações',
        }
        widgets = {
            'categoria': forms.Select(attrs={'class': 'form-select sigad-input', 'required': True}),
            'nome': forms.TextInput(attrs={'class': 'form-control sigad-input', 'placeholder': 'Ex: Arroz branco', 'required': True}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control sigad-input', 'min': 1, 'required': True}),
            'unidade': forms.Select(attrs={'class': 'form-select sigad-input', 'required': True}),
            'validade': forms.DateInput(attrs={'class': 'form-control sigad-input', 'type': 'date'}),
            'doador': forms.Select(attrs={'class': 'form-select sigad-input'}),
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
        self.fields['doador'].queryset = Doador.objects.order_by('nome')
        self.fields['doador'].empty_label = 'Selecione o doador…'

    def clean_categoria(self):
        v = self.cleaned_data.get('categoria')
        if not v:
            raise forms.ValidationError('Selecione uma categoria.')
        return v
