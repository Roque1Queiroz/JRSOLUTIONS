from django.db import models, transaction
from django.utils import timezone
from meigestao_app.core.models import BaseModel, Empresa
from meigestao_app.estoque.models import Produto, Estoque, MovimentacaoEstoque
from meigestao_app.almoxarifado.models import SaldoAlmoxarifado
from django.core.exceptions import ValidationError

class FichaTecnica(BaseModel):
    """
    Representa a 'receita' de composição de um produto acabado.
    """
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='fichas_tecnicas')
    produto_final = models.OneToOneField(Produto, on_delete=models.CASCADE, related_name='ficha_tecnica', 
                                        help_text="O produto que será fabricado.")
    descricao = models.TextField(blank=True, help_text="Instruções de montagem ou produção.")
    tempo_estimado_minutos = models.PositiveIntegerField(default=0, help_text="Tempo médio de produção em minutos.")
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Ficha Técnica'
        verbose_name_plural = 'Fichas Técnicas'

    def __str__(self):
        return f"Engenharia: {self.produto_final.nome}"

    def custo_total_materiais(self):
        """Calcula o custo total baseado na soma dos insumos na ficha."""
        total = 0
        for item in self.itens.all():
            total += item.produto_insumo.preco_custo * item.quantidade
        return total

class FichaTecnicaItem(models.Model):
    """
    Componentes individuais da Ficha Técnica.
    """
    ficha = models.ForeignKey(FichaTecnica, on_delete=models.CASCADE, related_name='itens')
    produto_insumo = models.ForeignKey(Produto, on_delete=models.CASCADE, help_text="Insumo retirado do almoxarifado.")
    quantidade = models.DecimalField(max_digits=10, decimal_places=3, help_text="Quantidade necessária para 1 unidade do produto final.")

    def __str__(self):
        return f"{self.quantidade} de {self.produto_insumo.nome}"

class OrdemProducao(BaseModel):
    """
    Documento de execução de produção.
    """
    STATUS_CHOICES = [
        ('ABERTA', 'Aberta / Planejada'),
        ('PRODUCAO', 'Em Produção'),
        ('FINALIZADA', 'Finalizada (Estoque Atualizado)'),
        ('CANCELADA', 'Cancelada'),
    ]

    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='ordens_producao')
    ficha_tecnica = models.ForeignKey(FichaTecnica, on_delete=models.PROTECT, related_name='ordens')
    quantidade_planejada = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ABERTA')
    
    # Custos e Tempos
    data_inicio = models.DateTimeField(null=True, blank=True)
    data_fim = models.DateTimeField(null=True, blank=True)
    custo_mao_obra_estimado = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, 
                                                help_text="Custo total de mão de obra para esta OP.")
    custo_materiais_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        verbose_name = 'Ordem de Produção'
        verbose_name_plural = 'Ordens de Produção'
        ordering = ['-criado_em']

    def __str__(self):
        return f"OP #{self.id} - {self.ficha_tecnica.produto_final.nome} ({self.quantidade_planejada} un)"

    def verificar_materiais_disponiveis(self):
        """
        Verifica se há saldo suficiente no Almoxarifado para todos os itens da ficha.
        """
        problemas = []
        for item in self.ficha_tecnica.itens.all():
            qtd_necessaria = item.quantidade * self.quantidade_planejada
            saldo_total = SaldoAlmoxarifado.objects.filter(
                local__empresa=self.empresa, 
                produto=item.produto_insumo
            ).aggregate(total=models.Sum('quantidade'))['total'] or 0
            
            if saldo_total < qtd_necessaria:
                problemas.append(f"{item.produto_insumo.nome} (Necessário: {qtd_necessaria}, Disponível: {saldo_total})")
        
        return problemas

    def finalizar_producao(self):
        """
        Executa a transformação física: Consome Insumos -> Gera Produto Acabado.
        """
        if self.status == 'FINALIZADA':
            raise ValidationError("Esta ordem de produção já foi finalizada.")

        problemas = self.verificar_materiais_disponiveis()
        if problemas:
            raise ValidationError(f"Saldo insuficiente no Almoxarifado para: {', '.join(problemas)}")

        with transaction.atomic():
            # 1. Consumir Insumos do Almoxarifado
            for item in self.ficha_tecnica.itens.all():
                qtd_pendente = item.quantidade * self.quantidade_planejada
                
                # Buscar saldos do item (ordenados por data para FIFO simbólico)
                saldos = SaldoAlmoxarifado.objects.filter(
                    local__empresa=self.empresa, 
                    produto=item.produto_insumo,
                    quantidade__gt=0
                ).order_by('criado_em')

                for saldo in saldos:
                    if qtd_pendente <= 0: break
                    
                    consumo = min(saldo.quantidade, qtd_pendente)
                    saldo.quantidade -= consumo
                    saldo.save()
                    qtd_pendente -= consumo

            # 2. Gerar Entrada no Estoque de Vendas
            produto_final = self.ficha_tecnica.produto_final
            MovimentacaoEstoque.objects.create(
                produto=produto_final,
                tipo_movimento='entrada',
                quantidade=self.quantidade_planejada,
                motivo=f"Entrada por Produção (OP #{self.id})"
            )

            # 3. Atualizar Dados da OP
            self.status = 'FINALIZADA'
            self.data_fim = timezone.now()
            self.custo_materiais_total = self.ficha_tecnica.custo_total_materiais() * self.quantidade_planejada
            self.save()
