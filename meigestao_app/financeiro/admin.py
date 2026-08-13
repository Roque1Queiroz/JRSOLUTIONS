from django.contrib import admin
from .models import Transacao, ReciboReembolso, ContaBancaria

@admin.register(ContaBancaria)
class ContaBancariaAdmin(admin.ModelAdmin):
    list_display = ('banco', 'agencia', 'conta', 'empresa', 'saldo', 'ativa')
    list_filter = ('empresa', 'ativa', 'banco')
    search_fields = ('banco', 'agencia', 'conta')

@admin.register(Transacao)
class TransacaoAdmin(admin.ModelAdmin):
    list_display = ('id', 'descricao', 'tipo', 'valor', 'data_transacao', 'paga', 'empresa')
    list_filter = ('tipo', 'paga', 'empresa')
    search_fields = ('descricao', 'categoria')

@admin.register(ReciboReembolso)
class ReciboReembolsoAdmin(admin.ModelAdmin):
    list_display = ('item', 'colaborador', 'valor', 'pago', 'empresa')
    list_filter = ('pago', 'empresa')
    search_fields = ('item', 'colaborador__usuario__username')
