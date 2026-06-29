from django.contrib import admin

from sigad_app.models import Beneficiado, Beneficiario, Distribuicao, ItemEstoque, LinhaDistribuicao


class LinhaDistribuicaoInline(admin.TabularInline):
    model = LinhaDistribuicao
    extra = 0


@admin.register(Distribuicao)
class DistribuicaoAdmin(admin.ModelAdmin):
    list_display = ('id', 'beneficiado', 'registrado_em')
    list_filter = ('registrado_em',)
    inlines = [LinhaDistribuicaoInline]


@admin.register(Beneficiario)
class BeneficiarioAdmin(admin.ModelAdmin):
    list_display = ('nome', 'telefone', 'email', 'criado_em')
    search_fields = ('nome', 'email', 'cpf')


@admin.register(Beneficiado)
class BeneficiadoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'telefone', 'email', 'ultima_distribuicao')
    search_fields = ('nome', 'email', 'cpf')


@admin.register(ItemEstoque)
class ItemEstoqueAdmin(admin.ModelAdmin):
    list_display = ('nome', 'categoria', 'quantidade', 'unidade', 'beneficiario', 'validade')
    list_filter = ('categoria',)
    search_fields = ('nome', 'beneficiario__nome')
