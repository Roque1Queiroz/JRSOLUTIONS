from django.contrib import admin
from django.utils.html import format_html
from .models import Setor, LocalArmazenamento, EnderecoArmazenamento, SaldoAlmoxarifado, RequisicaoInterna, ItemRequisicao

@admin.register(EnderecoArmazenamento)
class EnderecoArmazenamentoAdmin(admin.ModelAdmin):
    list_display = ('id', 'local', 'corredor', 'estante', 'prateleira', 'codigo_endereco', 'ver_qrcode', 'ver_codigo_barras')
    search_fields = ('codigo_endereco', 'local__nome', 'corredor', 'estante', 'prateleira')
    list_filter = ('local',)
    
    def ver_qrcode(self, obj):
        if obj.codigo_endereco:
            url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={obj.codigo_endereco}"
            return format_html('<a href="{}" target="_blank"><img src="{}" width="60" height="60" style="border-radius: 4px; border: 1px solid #ccc; padding: 2px;" title="Clique para ampliar/imprimir"/></a>', url, url)
        return "-"
    ver_qrcode.short_description = "QR Code (Local)"

    def ver_codigo_barras(self, obj):
        if obj.codigo_endereco:
            url = f"https://barcode.tec-it.com/barcode.ashx?data={obj.codigo_endereco}&code=Code128&translate-esc=true"
            return format_html('<a href="{}" target="_blank"><img src="{}" width="120" height="40" style="border-radius: 4px; border: 1px solid #ccc; padding: 2px;" title="Clique para ampliar/imprimir"/></a>', url, url)
        return "-"
    ver_codigo_barras.short_description = "Cód. Barras"

@admin.register(LocalArmazenamento)
class LocalArmazenamentoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'empresa', 'ativo')
    search_fields = ('nome',)

@admin.register(Setor)
class SetorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'responsavel', 'empresa')
    search_fields = ('nome',)

admin.site.register(SaldoAlmoxarifado)
admin.site.register(RequisicaoInterna)
admin.site.register(ItemRequisicao)
