from django.contrib import admin
from .models import Transacao, ReciboReembolso, ContaBancaria, CompromissoParcelado, ParcelaCompromisso

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


@admin.register(CompromissoParcelado)
class CompromissoParceladoAdmin(admin.ModelAdmin):
    list_display = ('descricao', 'credor', 'valor_total', 'numero_parcelas', 'empresa')
    search_fields = ('descricao', 'credor')


@admin.register(ParcelaCompromisso)
class ParcelaCompromissoAdmin(admin.ModelAdmin):
    list_display = ('referencia', 'numero', 'valor', 'vencimento', 'paga')
    search_fields = ('referencia',)
