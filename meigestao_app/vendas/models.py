from decimal import Decimal
from django.db import models, transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from meigestao_app.core.models import BaseModel, Empresa
from meigestao_app.clientes.models import Cliente

class Venda(BaseModel):
    """Modelo para Vendas"""
    
    STATUS_CHOICES = [
        ('rascunho', 'Rascunho'),
        ('confirmada', 'Confirmada'),
        ('entregue', 'Entregue'),
        ('cancelada', 'Cancelada'),
    ]
    
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='vendas')
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='vendas')
    
    data_venda = models.DateTimeField(default=timezone.now)
    descricao = models.TextField(blank=True)
    
    valor_subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    desconto = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='rascunho')
    observacoes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-data_venda']
        verbose_name = 'Venda'
        verbose_name_plural = 'Vendas'
    
    def __str__(self) -> str:
        return f"Venda #{self.id} - {self.cliente.nome}"

    def validar_mutacao_se_nao_liquidada(self) -> None:
        if not self.pk:
            return
        from meigestao_app.financeiro.models import Transacao

        if Transacao.objects.filter(venda_id=self.pk, paga=True).exists():
            raise ValidationError(
                'A venda possui uma transação paga. Estorne a transação antes de alterá-la.'
            )

    def calcular_total(self) -> Decimal:
        """Calcula o valor total da venda"""
        self.valor_subtotal = sum(
            (item.subtotal for item in self.itens.all()),
            Decimal('0.00'),
        )
        self.valor_total = self.valor_subtotal - (self.desconto or Decimal('0.00'))
        return self.valor_total

    def precisa_transacao_financeira(self) -> bool:
        return self.status in {'confirmada', 'entregue'} and self.valor_total > 0

    def recalcular_totais(self, persist: bool = True) -> Decimal:
        total = self.calcular_total()
        if persist and self.pk:
            self.save(update_fields=['valor_subtotal', 'valor_total', 'atualizado_em'])
        return total

    def _reverter_saldo_transacao(self, transacao) -> None:
        if not transacao.conta or not transacao.paga:
            return

        transacao.conta.refresh_from_db(fields=['saldo'])
        if transacao.tipo == 'receita':
            transacao.conta.saldo -= transacao.valor
        else:
            transacao.conta.saldo += transacao.valor
        transacao.conta.save(update_fields=['saldo'])

    def sincronizar_transacao_financeira(self) -> None:
        from meigestao_app.financeiro.models import Transacao

        try:
            transacao = self.transacao_financeira
        except Transacao.DoesNotExist:
            transacao = None

        if not self.precisa_transacao_financeira():
            if transacao:
                self._reverter_saldo_transacao(transacao)
                transacao.delete()
            return

        defaults = {
            'empresa': self.empresa,
            'tipo': 'receita',
            'categoria': 'Vendas',
            'descricao': f'Venda #{self.pk} - {self.cliente.nome}',
            'valor': self.valor_total,
            'data_transacao': self.data_venda.date(),
        }

        if transacao is None:
            Transacao.objects.create(venda=self, paga=False, **defaults)
            return

        campos_alterados = []
        for campo, valor in defaults.items():
            if getattr(transacao, campo) != valor:
                setattr(transacao, campo, valor)
                campos_alterados.append(campo)

        if campos_alterados:
            transacao.save(update_fields=campos_alterados + ['atualizado_em'])

    def gerar_nota_fiscal(self):
        """Gera uma Nota Fiscal a partir desta venda"""
        from meigestao_app.fiscal.models import NotaFiscal
        
        if hasattr(self, 'nota_fiscal'):
            raise ValueError('Esta venda já possui uma nota fiscal associada.')
        
        nf = NotaFiscal.objects.create(
            empresa=self.empresa,
            cliente=self.cliente,
            venda=self,
            numero=self.gerar_numero_nf(),
            serie='1',
            data_emissao=self.data_venda,
            descricao=f'Venda #{self.id}',
            valor_subtotal=self.valor_subtotal,
            valor_desconto=self.desconto,
            status='rascunho'
        )
        
        return nf
    
    def gerar_numero_nf(self) -> str:
        """Gera um número único para a NF"""
        from meigestao_app.fiscal.models import NotaFiscal
        
        agora = timezone.now()
        prefix = f"{agora.year}{agora.month:02d}"
        
        ultimo_numero = NotaFiscal.objects.filter(
            numero__startswith=prefix
        ).order_by('-numero').first()
        
        if ultimo_numero:
            # Extrair sequencial com safe cast
            try:
                sequencial = int(ultimo_numero.numero[-6:]) + 1
            except (ValueError, TypeError):
                sequencial = 1
        else:
            sequencial = 1
        
        return f"{prefix}{sequencial:06d}"

    def clean(self) -> None:
        super().clean()
        errors = {}
        if self.empresa_id and self.cliente_id and self.cliente.empresa_id != self.empresa_id:
            errors['cliente'] = 'O cliente deve pertencer à mesma empresa da venda.'
        if self.desconto is not None and self.desconto < 0:
            errors['desconto'] = 'O desconto não pode ser negativo.'
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs) -> None:
        with transaction.atomic():
            self.validar_mutacao_se_nao_liquidada()
            self.full_clean()
            super().save(*args, **kwargs)
            self.sincronizar_transacao_financeira()

    def delete(self, *args, **kwargs) -> None:
        from meigestao_app.financeiro.models import Transacao

        self.validar_mutacao_se_nao_liquidada()
        try:
            transacao = self.transacao_financeira
        except Transacao.DoesNotExist:
            transacao = None

        if transacao:
            self._reverter_saldo_transacao(transacao)
            transacao.delete()

        super().delete(*args, **kwargs)


class ItemVenda(models.Model):
    """Modelo para Itens de Venda"""
    
    venda = models.ForeignKey(Venda, on_delete=models.CASCADE, related_name='itens')
    produto_nome = models.CharField(max_length=255, default="", help_text="Nome do produto (no momento da venda)")
    produto_vinculado = models.ForeignKey(
        'estoque.Produto', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='itens_vendidos'
    )
    quantidade = models.PositiveIntegerField(default=1)
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    class Meta:
        verbose_name = 'Item de Venda'
        verbose_name_plural = 'Itens de Venda'
    
    def __str__(self) -> str:
        return f"{self.produto_nome} - {self.quantidade}x R$ {self.preco_unitario}"
    
    def clean(self) -> None:
        super().clean()
        errors = {}
        if (
            self.venda_id
            and self.produto_vinculado_id
            and self.produto_vinculado.empresa_id != self.venda.empresa_id
        ):
            errors['produto_vinculado'] = 'O produto deve pertencer à mesma empresa da venda.'
        if self.preco_unitario is not None and self.preco_unitario < 0:
            errors['preco_unitario'] = 'O preço unitário não pode ser negativo.'
        if self.quantidade is not None and self.quantidade <= 0:
            errors['quantidade'] = 'A quantidade deve ser maior que zero.'
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs) -> None:
        """Calcula o subtotal automaticamente"""
        with transaction.atomic():
            if self.venda_id:
                self.venda.validar_mutacao_se_nao_liquidada()
            self.full_clean()
            self.subtotal = self.quantidade * self.preco_unitario
            if kwargs.get('update_fields') is not None:
                kwargs['update_fields'] = set(kwargs['update_fields']) | {'subtotal'}
            super().save(*args, **kwargs)
            if self.venda_id:
                self.venda.recalcular_totais()

    def delete(self, *args, **kwargs) -> None:
        venda = self.venda
        venda.validar_mutacao_se_nao_liquidada()
        super().delete(*args, **kwargs)
        if venda.pk:
            venda.recalcular_totais()
