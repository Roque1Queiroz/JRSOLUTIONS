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


class RelatorioInteligencia(BaseModel):
    """Relatório financeiro gerado pelo worker noturno (Cientista Financeiro)."""

    empresa = models.ForeignKey(
        Empresa, on_delete=models.CASCADE, related_name='relatorios_inteligencia'
    )
    data_referencia = models.DateField(
        verbose_name='Data de Referência', db_index=True
    )
    dados_json = models.JSONField(
        verbose_name='Dados do Relatório',
        help_text='Conteúdo da análise: entradas, saídas, projeção, status e mensagem.',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['empresa', 'data_referencia'],
                name='uniq_relatorio_inteligencia_empresa_data',
            )
        ]
        ordering = ['-data_referencia']
        verbose_name = 'Relatório Inteligente'
        verbose_name_plural = 'Relatórios Inteligentes'

    def __str__(self):
        return f'Relatório {self.empresa} - {self.data_referencia}'



class CompromissoParcelado(BaseModel):
    """Gasto que nasce parcelado. Folha interna, nao boleto bancario."""

    empresa = models.ForeignKey(
        Empresa, on_delete=models.CASCADE, related_name='compromissos_parcelados',
        verbose_name='Empresa',
    )
    descricao = models.CharField(max_length=255, verbose_name='Descrição')
    credor = models.CharField(max_length=255, blank=True, verbose_name='Credor')
    valor_total = models.DecimalField(
        max_digits=15, decimal_places=2, verbose_name='Valor total',
    )
    numero_parcelas = models.PositiveIntegerField(verbose_name='Número de parcelas')
    primeiro_vencimento = models.DateField(verbose_name='Primeiro vencimento')
    observacao = models.TextField(blank=True, verbose_name='Observação')

    class Meta:
        ordering = ['-criado_em']
        verbose_name = 'Compromisso parcelado'
        verbose_name_plural = 'Compromissos parcelados'

    def __str__(self):
        return self.descricao

    def clean(self):
        from decimal import Decimal
        from django.core.exceptions import ValidationError
        erros = {}
        if self.valor_total is None or self.valor_total <= 0:
            erros['valor_total'] = 'O valor total tem que ser maior que zero.'
        if self.numero_parcelas is None or self.numero_parcelas < 2 or self.numero_parcelas > 120:
            erros['numero_parcelas'] = 'O numero de parcelas tem que ficar entre 2 e 120.'
        if erros:
            raise ValidationError(erros)

    def save(self, *args, **kwargs):
        novo = self.pk is None
        self.full_clean()
        super().save(*args, **kwargs)
        if novo:
            self.gerar_parcelas()

    def gerar_parcelas(self):
        from .parcelas import dividir_valor, referencia_parcela, somar_meses
        if self.parcelas.exists():
            return
        valores = dividir_valor(self.valor_total, self.numero_parcelas)
        for indice, valor in enumerate(valores, start=1):
            ParcelaCompromisso.objects.create(
                compromisso=self,
                numero=indice,
                valor=valor,
                vencimento=somar_meses(self.primeiro_vencimento, indice - 1),
                referencia=referencia_parcela(self.id, indice),
            )


class ParcelaCompromisso(BaseModel):
    """Uma parcela do compromisso e a folha interna (nosso boleto)."""

    compromisso = models.ForeignKey(
        CompromissoParcelado, on_delete=models.CASCADE, related_name='parcelas',
        verbose_name='Compromisso',
    )
    numero = models.PositiveIntegerField(verbose_name='Número')
    valor = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Valor')
    vencimento = models.DateField(verbose_name='Vencimento')
    paga = models.BooleanField(default=False, verbose_name='Paga')
    data_pagamento = models.DateField(null=True, blank=True, verbose_name='Data do pagamento')
    transacao = models.ForeignKey(
        Transacao, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='parcela_compromisso', verbose_name='Transação',
    )
    referencia = models.CharField(max_length=32, unique=True, verbose_name='Referência')

    class Meta:
        ordering = ['numero']
        verbose_name = 'Parcela de compromisso'
        verbose_name_plural = 'Parcelas de compromisso'
        constraints = [
            models.UniqueConstraint(
                fields=['compromisso', 'numero'],
                name='uniq_parcela_compromisso_numero',
            ),
        ]

    def __str__(self):
        return self.referencia

    @property
    def situacao(self):
        from django.utils import timezone
        if self.paga:
            return 'paga'
        if self.vencimento < timezone.localdate():
            return 'vencida'
        return 'em aberto'
