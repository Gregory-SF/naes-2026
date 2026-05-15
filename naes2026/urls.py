from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Importar urls dos apps
    path("", include("commex.urls")),
]
