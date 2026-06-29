from django.contrib import admin
from django.urls import path

from sigad_app.views import (
    BeneficiadoCreate,
    BeneficiadoDelete,
    BeneficiadoDetail,
    BeneficiadoList,
    BeneficiadoUpdate,
    BeneficiarioDelete,
    BeneficiarioUpdate,
    Dashboard,
    DistribuicaoDelete,
    DistribuicaoDetail,
    DistribuicaoList,
    DistribuicaoUpdate,
    ItemEstoqueDelete,
    ItemEstoqueDetail,
    ItemEstoqueList,
    ItemEstoqueUpdate,
    Landing,
    LinhaDistribuicaoDetail,
    LinhaDistribuicaoList,
    beneficiario_list,
    estoque,
    registrar_distribuicao,
    registrar_item,
    relatorios,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', Landing.as_view(), name='landing'),
    path('dashboard/', Dashboard.as_view(), name='dashboard'),

    # Beneficiário (quem DOA)
    path('beneficiarios/', beneficiario_list, name='beneficiario_list'),
    path('editar/beneficiario/<int:pk>/', BeneficiarioUpdate.as_view(), name='beneficiario_update'),
    path('excluir/beneficiario/<int:pk>/', BeneficiarioDelete.as_view(), name='beneficiario_delete'),

    # Beneficiado (quem RECEBE)
    path('beneficiados/', BeneficiadoList.as_view(), name='beneficiado_list'),
    path('cadastrar/beneficiado/', BeneficiadoCreate.as_view(), name='beneficiado_create'),
    path('ver/beneficiado/<int:pk>/', BeneficiadoDetail.as_view(), name='beneficiado_detail'),
    path('editar/beneficiado/<int:pk>/', BeneficiadoUpdate.as_view(), name='beneficiado_update'),
    path('excluir/beneficiado/<int:pk>/', BeneficiadoDelete.as_view(), name='beneficiado_delete'),

    # Estoque
    path('registrar-item/', registrar_item, name='registrar_item'),
    path('estoque/', estoque, name='estoque'),
    path('listar/itens-estoque/', ItemEstoqueList.as_view(), name='item_estoque_list'),
    path('editar/item-estoque/<int:pk>/', ItemEstoqueUpdate.as_view(), name='item_estoque_update'),
    path('excluir/item-estoque/<int:pk>/', ItemEstoqueDelete.as_view(), name='item_estoque_delete'),
    path('ver/item-estoque/<int:pk>/', ItemEstoqueDetail.as_view(), name='item_estoque_detail'),

    # Distribuição
    path('registrar-distribuicao/', registrar_distribuicao, name='registrar_distribuicao'),
    path('listar/distribuicoes/', DistribuicaoList.as_view(), name='distribuicao_list'),
    path('editar/distribuicao/<int:pk>/', DistribuicaoUpdate.as_view(), name='distribuicao_update'),
    path('excluir/distribuicao/<int:pk>/', DistribuicaoDelete.as_view(), name='distribuicao_delete'),
    path('ver/distribuicao/<int:pk>/', DistribuicaoDetail.as_view(), name='distribuicao_detail'),

    # Linhas de distribuição
    path('listar/linhas-distribuicao/', LinhaDistribuicaoList.as_view(), name='linha_distribuicao_list'),
    path('ver/linha-distribuicao/<int:pk>/', LinhaDistribuicaoDetail.as_view(), name='linha_distribuicao_detail'),

    # Relatórios
    path('relatorios/', relatorios, name='relatorios'),
]
