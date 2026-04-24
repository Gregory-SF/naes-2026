from django.urls import path

from .views import (
    ProjetoCreate,
    ProjetoUpdate,
    ProjetoDelete,
    ProjetoList,
    ProjetoDetail,
)

urlpatterns = [
    path('cadastrar/projeto/', ProjetoCreate.as_view(), name='projeto-create'),
    path('atualizar/projeto/<int:pk>/', ProjetoUpdate.as_view(), name='projeto-update'),
    path('excluir/projeto/<int:pk>/', ProjetoDelete.as_view(), name='projeto-delete'),
    path('listar/projeto/', ProjetoList.as_view(), name='projeto-list'),
    path('detalhar/projeto/<int:pk>/', ProjetoDetail.as_view(), name='projeto-detail'),
]
