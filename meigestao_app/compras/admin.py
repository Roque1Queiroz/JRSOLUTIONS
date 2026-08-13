from django.contrib import admin
from .models import Fornecedor, PedidoCompra, ItemPedidoCompra, Cotacao

admin.site.register(Fornecedor)
admin.site.register(PedidoCompra)
admin.site.register(ItemPedidoCompra)
admin.site.register(Cotacao)
