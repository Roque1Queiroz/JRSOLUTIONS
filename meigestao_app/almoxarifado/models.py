from django.db import models
from django.contrib.auth.models import User
from meigestao_app.core.models import BaseModel, Empresa
from meigestao_app.estoque.models import Produto

class Setor(BaseModel):
    """
    Representa um Setor ou Centro de Custo da empresa.
    Essencial para rastrear para onde os insumos estão indo.
    """
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='setores')
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)
    responsavel = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = 'Setor'
        verbose_name_plural = 'Setores'
        ordering = ['nome']

    def __str__(self):
        return f"{self.nome} ({self.empresa.nome})"

class LocalArmazenamento(BaseModel):
    """
    Representa um local físico de armazenamento (Almoxarifado, Depósito, Galpão).
    """
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='locais_armazenamento')
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Local de Armazenamento'
        verbose_name_plural = 'Locais de Armazenamento'

    def __str__(self):
        return self.nome

class EnderecoArmazenamento(BaseModel):
    """
    Representa um endereço específico dentro do local (Corredor, Estante, Prateleira).
    Ex: Corredor A, Prateleira 2, Gaveta 10.
    """
    local = models.ForeignKey(LocalArmazenamento, on_delete=models.CASCADE, related_name='enderecos')
    corredor = models.CharField(max_length=50, blank=True, null=True)
    estante = models.CharField(max_length=50, blank=True, null=True)
    prateleira = models.CharField(max_length=50, blank=True, null=True)
    
    # Identificador legível. Ex: CORR-A-EST-02
    codigo_endereco = models.SlugField(max_length=100, unique=True, help_text="Código único para o QR Code")

    class Meta:
        verbose_name = 'Endereço de Armazenamento'
        verbose_name_plural = 'Endereços de Armazenamento'
        ordering = ['local', 'corredor', 'estante', 'prateleira']

    def __str__(self):
        parts = []
        if self.corredor: parts.append(f"C:{self.corredor}")
        if self.estante: parts.append(f"E:{self.estante}")
        if self.prateleira: parts.append(f"P:{self.prateleira}")
        return f"{self.local.nome} > {' '.join(parts) or 'Geral'}"

class SaldoAlmoxarifado(BaseModel):
    """
    Controla o saldo de um produto em um local e endereço específico.
    """
    local = models.ForeignKey(LocalArmazenamento, on_delete=models.CASCADE, related_name='saldos')
    endereco = models.ForeignKey(EnderecoArmazenamento, on_delete=models.SET_NULL, null=True, blank=True, related_name='saldos')
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='saldos_almoxarifado')
    quantidade = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    quantidade_minima = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    class Meta:
        verbose_name = 'Saldo em Almoxarifado'
        verbose_name_plural = 'Saldos em Almoxarifado'
        unique_together = ('local', 'endereco', 'produto')

    def __str__(self):
        end_str = f" ({self.endereco})" if self.endereco else ""
        return f"{self.produto.nome} em {self.local.nome}{end_str}: {self.quantidade}"

class RequisicaoInterna(BaseModel):
    """
    Documento que registra a solicitação de materiais.
    """
    STATUS_CHOICES = [
        ('SOLICITADO', 'Solicitado'),
        ('APROVADO', 'Aprovado'),
        ('RECUSADO', 'Recusado'),
        ('ENTREGUE', 'Entregue'),
        ('CANCELADO', 'Cancelado'),
    ]

    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    solicitante = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requisicoes_feitas')
    setor = models.ForeignKey(Setor, on_delete=models.CASCADE, related_name='requisicoes')
    local_origem = models.ForeignKey(LocalArmazenamento, on_delete=models.CASCADE)
    
    justificativa = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SOLICITADO')
    
    data_aprovacao = models.DateTimeField(null=True, blank=True)
    aprovado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='requisicoes_aprovadas')
    
    observacoes_gestor = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Requisição Interna'
        verbose_name_plural = 'Requisições Internas'
        ordering = ['-criado_em']

    def __str__(self):
        return f"REQ #{self.id} - {self.setor.nome} ({self.get_status_display()})"

class ItemRequisicao(models.Model):
    """
    Itens específicos de uma requisição.
    """
    requisicao = models.ForeignKey(RequisicaoInterna, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade_solicitada = models.DecimalField(max_digits=10, decimal_places=2)
    quantidade_entregue = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    def __str__(self):
        return f"{self.produto.nome} ({self.quantidade_solicitada})"
