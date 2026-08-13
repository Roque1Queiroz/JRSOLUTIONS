from django.contrib import admin
from django.utils.html import format_html
from .models import Categoria, Produto, Estoque, MovimentacaoEstoque

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'sku', 'categoria', 'ver_codigo_barras')
    search_fields = ('nome', 'sku')
    list_filter = ('categoria', 'ativo')

    def ver_codigo_barras(self, obj):
        if obj.sku:
            url = f"https://barcode.tec-it.com/barcode.ashx?data={obj.sku}&code=Code128&translate-esc=true"
            return format_html('<a href="{}" target="_blank"><img src="{}" width="120" height="40" style="border-radius: 4px; border: 1px solid #ccc; padding: 2px;" title="Clique para ampliar/imprimir"/></a>', url, url)
        return "-"
    ver_codigo_barras.short_description = "Cód. Barras (SKU)"

admin.site.register(Categoria)
admin.site.register(Estoque)
admin.site.register(MovimentacaoEstoque)
