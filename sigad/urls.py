from django.contrib import admin
from django.urls import path

from sigad_app.views import *

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', Landing.as_view(), name='landing'),
    path('dashboard/', Dashboard.as_view(), name='dashboard'),

    path('cadastrar/beneficiario/', BeneficiarioCreate.as_view(), name='beneficiario_create'),
    path('listar/beneficiarios/', BeneficiarioList.as_view(), name='beneficiario_list'),
    path('editar/beneficiario/<int:pk>/', BeneficiarioUpdate.as_view(), name='beneficiario_update'),
    path('excluir/beneficiario/<int:pk>/', BeneficiarioDelete.as_view(), name='beneficiario_delete'),
    path('ver/beneficiario/<int:pk>/', BeneficiarioDetail.as_view(), name='beneficiario_detail'),

    path('cadastrar/item-estoque/', ItemEstoqueCreate.as_view(), name='item_estoque_create'),
    path('listar/itens-estoque/', ItemEstoqueList.as_view(), name='item_estoque_list'),
    path('editar/item-estoque/<int:pk>/', ItemEstoqueUpdate.as_view(), name='item_estoque_update'),
    path('excluir/item-estoque/<int:pk>/', ItemEstoqueDelete.as_view(), name='item_estoque_delete'),
    path('ver/item-estoque/<int:pk>/', ItemEstoqueDetail.as_view(), name='item_estoque_detail'),

    path('cadastrar/distribuicao/', DistribuicaoCreate.as_view(), name='distribuicao_create'),
    path('listar/distribuicoes/', DistribuicaoList.as_view(), name='distribuicao_list'),
    path('editar/distribuicao/<int:pk>/', DistribuicaoUpdate.as_view(), name='distribuicao_update'),
    path('excluir/distribuicao/<int:pk>/', DistribuicaoDelete.as_view(), name='distribuicao_delete'),
    path('ver/distribuicao/<int:pk>/', DistribuicaoDetail.as_view(), name='distribuicao_detail'),

    path('cadastrar/linha-distribuicao/', LinhaDistribuicaoCreate.as_view(), name='linha_distribuicao_create'),
    path('listar/linhas-distribuicao/', LinhaDistribuicaoList.as_view(), name='linha_distribuicao_list'),
    path('editar/linha-distribuicao/<int:pk>/', LinhaDistribuicaoUpdate.as_view(), name='linha_distribuicao_update'),
    path('excluir/linha-distribuicao/<int:pk>/', LinhaDistribuicaoDelete.as_view(), name='linha_distribuicao_delete'),
    path('ver/linha-distribuicao/<int:pk>/', LinhaDistribuicaoDetail.as_view(), name='linha_distribuicao_detail'),
]
