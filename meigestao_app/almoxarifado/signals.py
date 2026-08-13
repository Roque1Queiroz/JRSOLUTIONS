from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from .models import RequisicaoInterna, SaldoAlmoxarifado

@receiver(post_save, sender=RequisicaoInterna)
def processar_entrega_requisicao(sender, instance, created, **kwargs):
    """
    Quando o status da requisição muda para 'ENTREGUE', o sistema
    deduz automaticamente as quantidades do saldo do almoxarifado.
    """
    if instance.status == 'ENTREGUE':
        with transaction.atomic():
            for item in instance.itens.all():
                # Busca o saldo do produto no local de origem da requisição
                saldo, created_saldo = SaldoAlmoxarifado.objects.get_or_create(
                    local=instance.local_origem,
                    produto=item.produto,
                    defaults={'quantidade': 0}
                )
                
                # Se a quantidade entregue for maior que zero, deduz do saldo
                if item.quantidade_entregue > 0:
                    saldo.quantidade -= item.quantidade_entregue
                    saldo.save()
                    
                    # Log ou Auditoria pode ser adicionado aqui futuramente
