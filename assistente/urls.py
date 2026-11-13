from django.urls import path

from . import views

urlpatterns = [
    path('assistente/', views.assistente, name='assistente'),
    path('assistente/perguntar/', views.perguntar, name='assistente-perguntar'),
    path('assistente/limpar/', views.limpar, name='assistente-limpar'),
]
