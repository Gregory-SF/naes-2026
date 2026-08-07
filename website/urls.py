from django.urls import path
from .views import IndexView, ContatoView

from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, 


urlpatterns = [
    # path("url/navegador", Class._as_view(), name="nome_do_link"),
    path("", IndexView.as_view(), name="index"),
    path("contato/", ContatoView.as_view(), name="contato"),
    path("login/", LoginView.as_view(template_name="login.html"), name="login"),
    path("logout/", LogoutView.as_view(next_page="index"), name="logout"),  
    path("password_change/", PasswordChangeView.as_view(template_name="password_change.html"), name="password_change"),
]
