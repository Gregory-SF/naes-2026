from django.contrib import admin

from .models import ConfiguracaoIA, CotaUsuario, RequisicaoIA

admin.site.register(CotaUsuario)


@admin.register(ConfiguracaoIA)
class ConfiguracaoIAAdmin(admin.ModelAdmin):
    exclude = ('api_key',)  # a chave só é editada pela tela de configuração (criptografada)


@admin.register(RequisicaoIA)
class RequisicaoIAAdmin(admin.ModelAdmin):
    list_display = ('criado_em', 'usuario', 'origem', 'modelo', 'status', 'tokens_entrada', 'tokens_saida')
    list_filter = ('status', 'origem')
