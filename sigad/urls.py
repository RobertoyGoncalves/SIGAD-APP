from django.contrib import admin
from django.urls import path
from sigad_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.dashboard, name='dashboard'),
    path('registrar-item/', views.registrar_item, name='registrar_item'),
    path('registrar-distribuicao/', views.registrar_distribuicao, name='registrar_distribuicao'),
    path('estoque/', views.estoque, name='estoque'),
    path('beneficiarios/', views.beneficiarios, name='beneficiarios'),
    path('relatorios/', views.relatorios, name='relatorios'),
]
