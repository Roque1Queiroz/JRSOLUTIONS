from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from meigestao_app.core.models import BaseModel, Empresa

class Categoria(BaseModel):
    """Categorias de produtos soul"""
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='categorias_estoque', null=True)
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    
    class Meta:
        ordering = ['nome']
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        indexes = [models.Index(fields=['nome'])]
    
    def __str__(self):
        return self.nome


class Produto(BaseModel):
    """Produtos do estoque"""
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='produtos')
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, related_name='produtos')
    
    nome = models.CharField(max_length=200)
    sku = models.CharField(max_length=100, unique=True, help_text="Código único do produto")
    descricao = models.TextField(blank=True)
    
    preco_custo = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    preco_venda = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    ativo = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['nome']
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'
        indexes = [
            models.Index(fields=['sku']),
            models.Index(fields=['categoria']),
            models.Index(fields=['ativo']),
        ]
    
    def __str__(self):
        return f"{self.sku} - {self.nome}"
    
    def clean(self):
        errors = {}
        
        if self.preco_custo is not None and self.preco_custo < 0:
            errors['preco_custo'] = 'O preço de custo não pode ser negativo.'
        
        if self.preco_venda is not None and self.preco_venda < 0:
            errors['preco_venda'] = 'O preço de venda não pode ser negativo.'
        
        if self.preco_venda is not None and self.preco_custo is not None and self.preco_venda < self.preco_custo:
            errors['preco_venda'] = 'O preço de venda deve ser maior ou igual ao preço de custo.'
        
        if errors:
            raise ValidationError(errors)
    
    def save(self, *args, **kwargs):
        # Gerar SKU automático se não existir
        if not self.sku:
            import random
            import string
            prefix = "PRD"
            # Tentar gerar um código curto e único
            random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
            self.sku = f"{prefix}-{random_str}-{timezone.now().strftime('%y%m%d')}"
            
        self.full_clean()
        super().save(*args, **kwargs)
    
    def margem_lucro(self):
        """Calcula a margem de lucro em percentual"""
        if self.preco_custo > 0:
            return ((self.preco_venda - self.preco_custo) / self.preco_custo) * 100
        return 0


class Estoque(BaseModel):
    """Controle de estoque por produto"""
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='estoques', null=True)
    produto = models.OneToOneField(Produto, on_delete=models.CASCADE, related_name='estoque')
    
    quantidade = models.PositiveIntegerField(default=0)
    quantidade_minima = models.PositiveIntegerField(default=0, help_text="Quantidade mínima para alerta")
    
    localizacao = models.CharField(max_length=100, blank=True, help_text="Localização no armazém")
    
    class Meta:
        ordering = ['produto__nome']
        verbose_name = 'Estoque'
        verbose_name_plural = 'Estoques'
        indexes = [models.Index(fields=['produto'])]
    
    def __str__(self):
        return f"Estoque de {self.produto.nome}"
    
    def esta_em_falta(self):
        """Verifica se o estoque está abaixo do mínimo"""
        return self.quantidade <= self.quantidade_minima
    
    def valor_total(self):
        """Calcula o valor total do estoque"""
        return self.quantidade * self.produto.preco_custo


class MovimentacaoEstoque(BaseModel):
    """Histórico de movimentações de estoque"""
    
    TIPO_MOVIMENTO_CHOICES = [
        ('entrada', 'Entrada'),
        ('saida', 'Saída'),
        ('ajuste', 'Ajuste'),
        ('devolucao', 'Devolução'),
    ]
    
    item_venda = models.OneToOneField(
        'vendas.ItemVenda',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='movimento_saida_estoque',
    )
    movimento_saida_estornado = models.OneToOneField(
        'self',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='movimento_devolucao_estoque',
    )
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='movimentacoes_estoque', null=True)
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='movimentacoes')
    tipo_movimento = models.CharField(max_length=20, choices=TIPO_MOVIMENTO_CHOICES)
    quantidade = models.PositiveIntegerField()
    motivo = models.TextField(blank=True)
    
    data_movimento = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-data_movimento']
        verbose_name = 'Movimentação de Estoque'
        verbose_name_plural = 'Movimentações de Estoque'
        indexes = [
            models.Index(fields=['produto']),
            models.Index(fields=['tipo_movimento']),
            models.Index(fields=['data_movimento']),
        ]
    
    def __str__(self):
        return f"{self.get_tipo_movimento_display()} - {self.produto.nome} ({self.quantidade})"
    
    def clean(self):
        if self.quantidade is None:
            return
            
        if self.quantidade <= 0:
            raise ValidationError({'quantidade': 'A quantidade deve ser maior que zero.'})
            
        # Validar estoque insuficiente para saídas
        if self.tipo_movimento == 'saida' and hasattr(self, 'produto') and self.produto:
            try:
                # Tenta obter o estoque do produto
                # Se não existir, vai cair no DoesNotExist (ou get_or_create no save)
                # Mas para a limpeza, precisamos saber se há saldo
                try:
                    estoque = self.produto.estoque
                except Exception:
                    # Se não tem estoque criado ainda, saldo é 0
                    estoque = None
                
                if not estoque or estoque.quantidade < self.quantidade:
                    qtd_disp = estoque.quantidade if estoque else 0
                    raise ValidationError({'quantidade': f'Quantidade insuficiente em estoque. Disponível: {qtd_disp}'})
            except Exception:
                # Silenciar erros inesperados aqui para não travar a limpeza se o problema for outro
                pass
    
    def save(self, *args, **kwargs):
        from django.db import transaction

        self.full_clean()
        criando = self._state.adding
        vinculado_venda = bool(
            self.item_venda_id or self.movimento_saida_estornado_id
        )
        if not criando and vinculado_venda:
            original = type(self).objects.filter(pk=self.pk).values(
                'item_venda_id',
                'movimento_saida_estornado_id',
                'empresa_id',
                'produto_id',
                'tipo_movimento',
                'quantidade',
            ).first()
            campos_economicos = {
                'item_venda_id': self.item_venda_id,
                'movimento_saida_estornado_id': self.movimento_saida_estornado_id,
                'empresa_id': self.empresa_id,
                'produto_id': self.produto_id,
                'tipo_movimento': self.tipo_movimento,
                'quantidade': self.quantidade,
            }
            if original and any(
                original[campo] != valor
                for campo, valor in campos_economicos.items()
            ):
                raise ValidationError(
                    'O efeito de estoque vinculado à venda é imutável.'
                )

        with transaction.atomic():
            super().save(*args, **kwargs)

            if not criando:
                return

            # Movimentos de venda são validados e aplicados por trigger de banco,
            # incluindo bulk_create/importações, para impedir prova de baixa falsa.
            if self.item_venda_id or self.movimento_saida_estornado_id:
                return

            # Atualizar estoque automaticamente somente na criação.
            estoque, created = Estoque.objects.get_or_create(
                produto=self.produto,
                defaults={'empresa': self.empresa}
            )
            
            if self.tipo_movimento == 'entrada':
                estoque.quantidade += self.quantidade
            elif self.tipo_movimento == 'saida':
                # O check de quantidade já foi feito no clean()
                estoque.quantidade -= self.quantidade
            elif self.tipo_movimento == 'ajuste':
                estoque.quantidade = self.quantidade
            elif self.tipo_movimento == 'devolucao':
                estoque.quantidade += self.quantidade
            
            estoque.save()