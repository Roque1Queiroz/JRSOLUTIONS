# -*- coding: utf-8 -*-

from django.db import models
from django.utils import timezone
from meigestao_app.core.models import BaseModel, Empresa

class ContaBancaria(BaseModel):
    """Modelo de Conta Bancária."""
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='contas_bancarias')
    banco = models.CharField(max_length=100)
    agencia = models.CharField(max_length=20)
    conta = models.CharField(max_length=20)
    saldo = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    ativa = models.BooleanField(default=True)

    class Meta:
        ordering = ['banco']
        verbose_name = 'Conta Bancária'
        verbose_name_plural = 'Contas Bancárias'

    def __str__(self):
        return f'{self.banco} - {self.agencia}/{self.conta}'


class Transacao(BaseModel):
    """Modelo de Transação Financeira."""
    TIPO_CHOICES = [
        ('receita', 'Receita'),
        ('despesa', 'Despesa'),
    ]

    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='transacoes')
    venda = models.OneToOneField(
        'vendas.Venda',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='transacao_financeira',
    )
    conta = models.ForeignKey(ContaBancaria, on_delete=models.SET_NULL, null=True, blank=True, related_name='transacoes')
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    categoria = models.CharField(max_length=50)
    descricao = models.CharField(max_length=500)
    valor = models.DecimalField(max_digits=15, decimal_places=2)
    data_transacao = models.DateField()
    data_vencimento = models.DateField(blank=True, null=True)
    paga = models.BooleanField(default=False)

    class Meta:
        ordering = ['-data_transacao']
        verbose_name = 'Transação'
        verbose_name_plural = 'Transações'

    def __str__(self):
        return f'{self.tipo.upper()} - {self.descricao} - R$ {self.valor}'


class ReciboReembolso(BaseModel):
    PRIORIDADE_CHOICES = [
        ('alta', '🔴 Alta'),
        ('media', '🟡 Média'),
        ('baixa', '🟢 Baixa'),
    ]

    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='reembolsos')
    colaborador = models.ForeignKey('usuarios.Perfil', on_delete=models.SET_NULL, null=True, blank=True, related_name='reembolsos', verbose_name="Colaborador")
    nome_solicitante = models.CharField(max_length=255, blank=True, null=True, verbose_name="Nome do Solicitante (Manual)")
    prioridade = models.CharField(max_length=10, choices=PRIORIDADE_CHOICES, default='media', verbose_name="Prioridade")
    item = models.CharField(max_length=255, verbose_name="Item/Descrição")
    valor = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Valor")
    data_compra = models.DateField(default=timezone.now, verbose_name="Data da Compra")
    foto_recibo = models.FileField(upload_to='reembolsos/%Y/%m/', blank=True, null=True, verbose_name="Comprovante (Imagem ou PDF)")
    pago = models.BooleanField(default=False, verbose_name="Reembolsado?")
    transacao = models.OneToOneField(Transacao, on_delete=models.SET_NULL, null=True, blank=True, related_name='reembolso_origem', verbose_name="Transação Vinculada")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")

    class Meta:
        ordering = ['-data_compra']
        verbose_name = 'Recibo de Reembolso'
        verbose_name_plural = 'Recibos de Reembolso'

    def __str__(self):
        return f'{self.item} - R$ {self.valor} ({self.colaborador.usuario.first_name})'
