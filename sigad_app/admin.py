from django.contrib import admin

from sigad_app.models import Beneficiario, Distribuicao, ItemEstoque, LinhaDistribuicao


class LinhaDistribuicaoInline(admin.TabularInline):
    model = LinhaDistribuicao
    extra = 0


@admin.register(Distribuicao)
class DistribuicaoAdmin(admin.ModelAdmin):
    list_display = ('id', 'beneficiario', 'registrado_em')
    list_filter = ('registrado_em',)
    inlines = [LinhaDistribuicaoInline]


admin.site.register(Beneficiario)
admin.site.register(ItemEstoque)
