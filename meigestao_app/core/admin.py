from django.contrib import admin
from .models import Empresa

@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cnpj', 'plano', 'ativa')
    list_filter = ('plano', 'ativa')
    search_fields = ('nome', 'cnpj')


