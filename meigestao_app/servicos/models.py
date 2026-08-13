from django.db import models
from django.utils import timezone
from meigestao_app.core.models import BaseModel, Empresa
from meigestao_app.clientes.models import Cliente
from django.contrib.auth import get_user_model

User = get_user_model()

class OrdemServico(BaseModel):
    """Modelo para Ordens de Serviço (Externas, Manufatura ou Manutenção)."""
    
    TIPO_CHOICES = [
        ('EXTERNO', 'Serviço ao Cliente'),
        ('MANUFATURA', 'Manufatura Interna'),
        ('MANUTENCAO', 'Manutenção Interna'),
    ]
    
    STATUS_CHOICES = [
        ('ABERTA', 'Aberta'),
        ('EXECUCAO', 'Em Execução'),
        ('FINALIZADA', 'Finalizada'),
        ('CANCELADA', 'Cancelada'),
    ]
    
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='ordens_servico')
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='ordens_servico', null=True, blank=True)
    solicitante = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='os_solicitadas')
    responsavel = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='os_atribuidas')
    
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='EXTERNO')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ABERTA')
    
    data_inicio = models.DateTimeField(default=timezone.now)
    data_fim = models.DateTimeField(null=True, blank=True)
    
    descricao = models.TextField(verbose_name="Descrição do Problema/Pedido")
    laudo_tecnico = models.TextField(blank=True, verbose_name="Laudo Técnico/Ações Realizadas")
    
    valor_servico = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    valor_materiais = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    class Meta:
        verbose_name = 'Ordem de Serviço'
        verbose_name_plural = 'Ordens de Serviço'
        ordering = ['-criado_em']

    def __str__(self):
        return f"OS #{self.id} - {self.get_tipo_display()} ({self.status})"

    def calcular_materiais(self):
        """Soma o valor dos materiais usados na OS."""
        self.valor_materiais = self.itens.aggregate(total=models.Sum('valor_total'))['total'] or 0
        self.valor_total = self.valor_servico + self.valor_materiais
        self.save(update_fields=['valor_materiais', 'valor_total'])

class ItemOrdemServico(models.Model):
    """Itens consumidos do almoxarifado durante a OS."""
    
    os = models.ForeignKey(OrdemServico, on_delete=models.CASCADE, related_name='itens')
    material = models.ForeignKey('almoxarifado.SaldoAlmoxarifado', on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(default=1)
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    baixa_estoque = models.BooleanField(default=False, help_text="Se a baixa no estoque foi processada.")

    def save(self, *args, **kwargs):
        self.valor_total = self.quantidade * self.preco_unitario
        super().save(*args, **kwargs)
        self.os.calcular_materiais()

    class Meta:
        verbose_name = 'Item da OS'
        verbose_name_plural = 'Itens da OS'
