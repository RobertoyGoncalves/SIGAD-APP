import django.conf as _conf
from django.contrib import admin
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)
from django.urls import include, path, reverse_lazy

from sigad_app.views import (
    BeneficiadoCreate,
    BeneficiadoDelete,
    BeneficiadoDetail,
    BeneficiadoList,
    BeneficiadoUpdate,
    DoadorCreate,
    DoadorDelete,
    DoadorUpdate,
    CadastroUsuarioView,
    Dashboard,
    DistribuicaoDelete,
    DistribuicaoDetail,
    DistribuicaoList,
    DistribuicaoUpdate,
    EstoqueBaixoView,
    ItemEstoqueCreate,
    ItemEstoqueDelete,
    ItemEstoqueDetail,
    ItemEstoqueList,
    ItemEstoqueUpdate,
    Landing,
    LinhaDistribuicaoDetail,
    LinhaDistribuicaoList,
    SigadLoginView,
    SigadLogoutView,
    SigadPasswordChangeDoneView,
    SigadPasswordChangeView,
    UsuarioListView,
    alternar_admin,
    alternar_ativo,
    doador_list,
    estoque,
    registrar_distribuicao,
    relatorios,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', Landing.as_view(), name='landing'),
    path('login/', SigadLoginView.as_view(), name='login'),
    path('cadastro/', CadastroUsuarioView.as_view(), name='cadastro_usuario'),
    path('logout/', SigadLogoutView.as_view(), name='logout'),
    path('senha/alterar/', SigadPasswordChangeView.as_view(), name='password_change'),
    path('senha/alterada/', SigadPasswordChangeDoneView.as_view(), name='password_change_done'),

    # Bug 3 — fluxo de recuperação de senha (views prontas do Django)
    path('senha/esqueci/', PasswordResetView.as_view(
        template_name='sigad_app/form.html',
        extra_context={'titulo': 'Recuperar senha', 'botao': 'Enviar e-mail', 'cancelar_url': reverse_lazy('login')},
        success_url=reverse_lazy('password_reset_done'),
    ), name='password_reset'),
    path('senha/esqueci/enviado/', PasswordResetDoneView.as_view(
        template_name='sigad_app/password_reset_done.html',
    ), name='password_reset_done'),
    path('senha/redefinir/<uidb64>/<token>/', PasswordResetConfirmView.as_view(
        template_name='sigad_app/form.html',
        extra_context={'titulo': 'Nova senha', 'botao': 'Salvar nova senha', 'cancelar_url': reverse_lazy('login')},
        success_url=reverse_lazy('password_reset_complete'),
    ), name='password_reset_confirm'),
    path('senha/redefinida/', PasswordResetCompleteView.as_view(
        template_name='sigad_app/password_reset_complete.html',
    ), name='password_reset_complete'),

    path('dashboard/', Dashboard.as_view(), name='dashboard'),

    # Doador (quem DOA)
    path('doadores/', doador_list, name='doador_list'),
    path('cadastrar/doador/', DoadorCreate.as_view(), name='doador_create'),
    path('editar/doador/<int:pk>/', DoadorUpdate.as_view(), name='doador_update'),
    path('excluir/doador/<int:pk>/', DoadorDelete.as_view(), name='doador_delete'),

    # Beneficiado (quem RECEBE)
    path('beneficiados/', BeneficiadoList.as_view(), name='beneficiado_list'),
    path('cadastrar/beneficiado/', BeneficiadoCreate.as_view(), name='beneficiado_create'),
    path('ver/beneficiado/<int:pk>/', BeneficiadoDetail.as_view(), name='beneficiado_detail'),
    path('editar/beneficiado/<int:pk>/', BeneficiadoUpdate.as_view(), name='beneficiado_update'),
    path('excluir/beneficiado/<int:pk>/', BeneficiadoDelete.as_view(), name='beneficiado_delete'),

    # Estoque
    path('registrar-item/', ItemEstoqueCreate.as_view(), name='registrar_item'),
    path('estoque/', estoque, name='estoque'),
    path('listar/itens-estoque/', ItemEstoqueList.as_view(), name='item_estoque_list'),
    path('editar/item-estoque/<int:pk>/', ItemEstoqueUpdate.as_view(), name='item_estoque_update'),
    path('excluir/item-estoque/<int:pk>/', ItemEstoqueDelete.as_view(), name='item_estoque_delete'),
    path('ver/item-estoque/<int:pk>/', ItemEstoqueDetail.as_view(), name='item_estoque_detail'),
    # Req 1 — view informativa: itens com estoque baixo (não é CRUD)
    path('estoque/alerta/', EstoqueBaixoView.as_view(), name='estoque_alerta'),

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

    # Usuários (superuser / grupo Gestores)
    path('usuarios/', UsuarioListView.as_view(), name='usuario_list'),
    path('usuarios/<int:pk>/alternar-admin/', alternar_admin, name='alternar_admin'),
    path('usuarios/<int:pk>/alternar-ativo/', alternar_ativo, name='alternar_ativo'),
]

# Req 4 — Debug Toolbar só em desenvolvimento (nunca em produção)
if _conf.settings.DEBUG:
    urlpatterns += [path('__debug__/', include('debug_toolbar.urls'))]
