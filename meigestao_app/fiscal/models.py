from django.db import IntegrityError, models, transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from meigestao_app.core.models import BaseModel, Empresa
from meigestao_app.clientes.models import Cliente
from meigestao_app.vendas.models import Venda


class NotaFiscalSequencia(models.Model):
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name='sequencias_notas_fiscais',
    )
    serie = models.CharField(max_length=5, default='1')
    ultimo_numero = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['empresa', 'serie'],
                name='fiscal_seq_empresa_serie_uniq',
            )
        ]


class NotaFiscal(BaseModel):
    """Modelo para Notas Fiscais com validações de negócio"""
    
    STATUS_CHOICES = [
        ('rascunho', 'Rascunho'),
        ('emitida', 'Emitida'),
        ('cancelada', 'Cancelada'),
    ]
    
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='notas_fiscais')
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='notas_fiscais')
    venda = models.OneToOneField(Venda, on_delete=models.SET_NULL, null=True, blank=True, related_name='nota_fiscal')
    
    numero = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        help_text="Número da NF",
    )
    serie = models.CharField(max_length=5, default='1', help_text="Série da NF")
    data_emissao = models.DateTimeField(default=timezone.now)
    data_saida = models.DateTimeField(null=True, blank=True)
    
    descricao = models.TextField(blank=True, help_text="Descrição dos itens")
    valor_subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    valor_desconto = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    valor_icms = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    valor_ipi = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='rascunho')
    observacoes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-data_emissao']
        verbose_name = 'Nota Fiscal'
        verbose_name_plural = 'Notas Fiscais'
        indexes = [
            models.Index(fields=['numero', 'serie']),
            models.Index(fields=['cliente', 'data_emissao']),
            models.Index(fields=['status']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['empresa', 'serie', 'numero'],
                name='fiscal_nf_empresa_serie_numero_uniq',
            ),
            models.CheckConstraint(
                check=(
                    ~models.Q(status__in=['emitida', 'cancelada'])
                    | (
                        models.Q(numero__isnull=False)
                        & ~models.Q(numero='')
                    )
                ),
                name='fiscal_nf_status_final_exige_numero',
            ),
        ]
    
    def __str__(self):
        return f"NF {self.numero}/{self.serie} - {self.cliente.nome}"
    
    def clean(self):
        """Validações de negócio"""
        errors = {}
        
        # Validar número da NF
        if self.status in ['emitida', 'cancelada'] and (
            not self.numero or self.numero.strip() == ''
        ):
            errors['numero'] = 'O número da NF é obrigatório para notas emitidas ou canceladas.'
        
        # Validar série
        if not self.serie or self.serie.strip() == '':
            errors['serie'] = 'A série é obrigatória.'
        
        # Validar valores
        if self.valor_subtotal < 0:
            errors['valor_subtotal'] = 'O subtotal não pode ser negativo.'
        
        if self.valor_desconto < 0:
            errors['valor_desconto'] = 'O desconto não pode ser negativo.'
        
        if self.valor_desconto > self.valor_subtotal:
            errors['valor_desconto'] = 'O desconto não pode ser maior que o subtotal.'
        
        if self.valor_icms < 0:
            errors['valor_icms'] = 'O ICMS não pode ser negativo.'
        
        if self.valor_ipi < 0:
            errors['valor_ipi'] = 'O IPI não pode ser negativo.'
        
        # Validar data de saída
        if self.data_saida and self.data_saida < self.data_emissao:
            errors['data_saida'] = 'A data de saída não pode ser anterior à data de emissão.'
        
        # Validar cliente
        if not self.cliente:
            errors['cliente'] = 'O cliente é obrigatório.'
        elif self.empresa_id and self.cliente.empresa_id != self.empresa_id:
            errors['cliente'] = 'O cliente deve pertencer à mesma empresa da nota fiscal.'

        if self.venda_id:
            if self.empresa_id and self.venda.empresa_id != self.empresa_id:
                errors['venda'] = 'A venda deve pertencer à mesma empresa da nota fiscal.'
            elif self.cliente_id and self.venda.cliente_id != self.cliente_id:
                errors['venda'] = 'A venda deve pertencer ao cliente informado na nota fiscal.'
        
        if errors:
            raise ValidationError(errors)
    
    def save(self, *args, **kwargs):
        """Salvar com validações e cálculos automáticos"""
        self.full_clean()
        self.calcular_total()
        super().save(*args, **kwargs)
    
    def calcular_total(self):
        """Calcula o valor total da NF"""
        self.valor_total = (
            self.valor_subtotal 
            - self.valor_desconto 
            + self.valor_icms 
            + self.valor_ipi
        )
        return self.valor_total
    
    def pode_editar(self):
        """Verifica se a NF pode ser editada"""
        return self.status in ['rascunho', 'emitida']
    
    def pode_cancelar(self):
        """Verifica se a NF pode ser cancelada"""
        return self.status == 'emitida'
    
    def emitir(self):
        """Emite a nota fiscal (muda status para emitida)"""
        with transaction.atomic():
            nota = NotaFiscal.objects.select_for_update().get(pk=self.pk)
            if nota.status != 'rascunho':
                raise ValidationError('Apenas rascunhos podem ser emitidos.')

            sequencia = (
                NotaFiscalSequencia.objects.select_for_update()
                .filter(empresa=nota.empresa, serie=nota.serie)
                .first()
            )
            if sequencia is None:
                try:
                    with transaction.atomic():
                        sequencia = NotaFiscalSequencia.objects.create(
                            empresa=nota.empresa,
                            serie=nota.serie,
                            ultimo_numero=0,
                        )
                except IntegrityError:
                    sequencia = (
                        NotaFiscalSequencia.objects.select_for_update().get(
                            empresa=nota.empresa,
                            serie=nota.serie,
                        )
                    )

            sequencia.ultimo_numero += 1
            sequencia.save(update_fields=['ultimo_numero'])

            nota.numero = str(sequencia.ultimo_numero)
            nota.status = 'emitida'
            nota.save(update_fields=['numero', 'status', 'atualizado_em'])
            self.numero = nota.numero
            self.status = nota.status
    
    def cancelar(self):
        """Cancela a nota fiscal"""
        if not self.pode_cancelar():
            raise ValidationError('Apenas notas fiscais emitidas podem ser canceladas.')
        self.status = 'cancelada'
        self.save()