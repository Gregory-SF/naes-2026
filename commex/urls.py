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
]
