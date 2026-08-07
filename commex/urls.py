from django.urls import path

from .views import *

urlpatterns = [
    path("", IndexView.as_view(), name="index"),

    path('cadastrar/projeto/', ProjetoCreate.as_view(), name='projeto-create'),
    path('atualizar/projeto/<int:pk>/', ProjetoUpdate.as_view(), name='projeto-update'),
    path('excluir/projeto/<int:pk>/', ProjetoDelete.as_view(), name='projeto-delete'),
    path('listar/projeto/', ProjetoList.as_view(), name='projeto-list'),
    path('detalhar/projeto/<int:pk>/', ProjetoDetail.as_view(), name='projeto-detail'),

    path('cadastrar/equipe/', EquipeCreate.as_view(), name='equipe-create'),
    path('atualizar/equipe/<int:pk>/', EquipeUpdate.as_view(), name='equipe-update'),
    path('excluir/equipe/<int:pk>/', EquipeDelete.as_view(), name='equipe-delete'),
    path('listar/equipe/', EquipeList.as_view(), name='equipe-list'),
    path('detalhar/equipe/<int:pk>/', EquipeDetail.as_view(), name='equipe-detail'),
    path('remover/membro/<int:pk>/', membro_delete, name='membro-delete'),

    path('cadastrar/sprint/', SprintCreate.as_view(), name='sprint-create'),
    path('atualizar/sprint/<int:pk>/', SprintUpdate.as_view(), name='sprint-update'),
    path('listar/sprint/', SprintList.as_view(), name='sprint-list'),
    path('detalhar/sprint/<int:pk>/', SprintDetail.as_view(), name='sprint-detail'),

    path('configuracoes/globais/', configuracoes_globais, name='configuracoes-globais'),
    path('configuracoes/remover-token/', configuracoes_remover_token, name='configuracoes-remover-token'),

    path('analysis/branches/', analysis_branches, name='analysis-branches'),
    path('analysis/start/', analysis_start, name='analysis-start'),
    path('analysis/status/', analysis_status, name='analysis-status-list'),
    path('analysis/status/<int:pk>/', analysis_status, name='analysis-status'),
]
