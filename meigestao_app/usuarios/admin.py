from django.contrib import admin
from .models import Perfil

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'empresa', 'permissao', 'ativo')
    list_filter = ('empresa', 'permissao', 'ativo')
    search_fields = ('usuario__username', 'usuario__first_name', 'usuario__last_name', 'empresa__nome')