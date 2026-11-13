from django.urls import path

from . import views

app_name = 'ia'

urlpatterns = [
    path('requisicoes/', views.RequisicaoList.as_view(), name='requisicoes'),
    path('configuracao/', views.configuracao, name='configuracao'),
    path('configuracao/testar/', views.testar_conexao, name='testar-conexao'),
    path('usuarios/', views.usuarios, name='usuarios'),
    path('usuarios/<int:pk>/', views.usuario_editar, name='usuario-editar'),
    path('meu-consumo/', views.meu_consumo, name='meu-consumo'),
]
