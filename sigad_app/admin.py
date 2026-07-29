from django.contrib import admin
# Req 2 — Group já é registrado automaticamente pelo django.contrib.auth em
# /admin/auth/group/; não precisamos re-registrar, apenas garantir que
# 'django.contrib.auth' está em INSTALLED_APPS (já está em settings.py).

from sigad_app.models import Beneficiado, Distribuicao, Doador, ItemEstoque, LinhaDistribuicao


class LinhaDistribuicaoInline(admin.TabularInline):
    model = LinhaDistribuicao
    extra = 0


@admin.register(Distribuicao)
class DistribuicaoAdmin(admin.ModelAdmin):
    list_display = ('id', 'beneficiado', 'usuario', 'registrado_em')
    list_filter = ('registrado_em', 'usuario')
    inlines = [LinhaDistribuicaoInline]


@admin.register(Doador)
class DoadorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'telefone', 'email', 'usuario', 'criado_em')
    list_filter = ('usuario',)
    search_fields = ('nome', 'email', 'cpf')


@admin.register(Beneficiado)
class BeneficiadoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'telefone', 'email', 'usuario', 'ultima_distribuicao')
    list_filter = ('usuario',)
    search_fields = ('nome', 'email', 'cpf')


@admin.register(ItemEstoque)
class ItemEstoqueAdmin(admin.ModelAdmin):
    list_display = ('nome', 'categoria', 'quantidade', 'unidade', 'doador', 'usuario', 'validade')
    list_filter = ('categoria', 'usuario')
    search_fields = ('nome', 'doador__nome')
