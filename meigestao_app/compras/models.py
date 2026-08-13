from django.db import models
from django.db.models import Q
from meigestao_app.core.models import BaseModel, Empresa
from meigestao_app.estoque.models import Produto

class Fornecedor(BaseModel):
    """Modelo de Fornecedores."""
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='fornecedores')
    nome = models.CharField(max_length=255)
    cnpj = models.CharField(max_length=18, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    endereco = models.CharField(max_length=500, blank=True, null=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Fornecedor'
        verbose_name_plural = 'Fornecedores'
        ordering = ['nome']

    def __str__(self):
        return self.nome

class PedidoCompra(BaseModel):
    """Solicitação ou Pedido de Compra."""
    STATUS_CHOICES = [
        ('SOLICITADO', 'Solicitado'),
        ('COTACAO', 'Em Cotação (Mapa)'),
        ('APROVADO', 'Aprovado'),
        ('RECEBIDO', 'Recebido/No Estoque'),
        ('CANCELADO', 'Cancelado'),
    ]
    
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='pedidos_compra')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SOLICITADO')
    data_prevista = models.DateField(null=True, blank=True)
    observacoes = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Pedido de Compra'
        verbose_name_plural = 'Pedidos de Compra'
        ordering = ['-criado_em']

    def __str__(self):
        return f"Pedido #{self.id} ({self.status})"

class Cotacao(BaseModel):
    """Orçamentos para um Pedido de Compra."""
    pedido_compra = models.ForeignKey(PedidoCompra, on_delete=models.CASCADE, related_name='cotacoes')
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.CASCADE, related_name='cotacoes')
    
    valor_total = models.DecimalField(max_digits=12, decimal_places=2)
    prazo_entrega_dias = models.PositiveIntegerField(verbose_name="Prazo (Dias)")
    condicoes_pagamento = models.CharField(max_length=255, blank=True)
    
    vencedor = models.BooleanField(default=False)
    arquivo_anexo = models.FileField(upload_to='compras/cotacoes/', blank=True, null=True)

    class Meta:
        verbose_name = 'Cotação'
        verbose_name_plural = 'Cotações'
        ordering = ['valor_total', 'prazo_entrega_dias']
        constraints = [
            models.UniqueConstraint(
                fields=['pedido_compra'],
                condition=Q(vencedor=True),
                name='compras_um_vencedor_por_pedido',
            ),
        ]

class ItemPedidoCompra(models.Model):
    """Itens solicitados para compra."""
    pedido_compra = models.ForeignKey(PedidoCompra, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f"{self.quantidade}x {self.produto.nome}"
