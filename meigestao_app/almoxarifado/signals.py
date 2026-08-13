from django.db import transaction
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import RequisicaoInterna, SaldoAlmoxarifado


@receiver(pre_save, sender=RequisicaoInterna)
def registrar_status_anterior_requisicao(sender, instance, **kwargs):
    if not instance.pk:
        instance._status_anterior = None
        return

    instance._status_anterior = (
        sender.objects.filter(pk=instance.pk)
        .values_list("status", flat=True)
        .first()
    )


@receiver(post_save, sender=RequisicaoInterna)
def processar_entrega_requisicao(sender, instance, created, **kwargs):
    """Deduz o saldo uma única vez, na transição para ENTREGUE."""
    status_anterior = getattr(instance, "_status_anterior", None)
    if instance.status != "ENTREGUE" or status_anterior == "ENTREGUE":
        return

    with transaction.atomic():
        for item in instance.itens.all():
            saldo, _ = SaldoAlmoxarifado.objects.select_for_update().get_or_create(
                local=instance.local_origem,
                produto=item.produto,
                defaults={"quantidade": 0},
            )

            if item.quantidade_entregue > 0:
                saldo.quantidade -= item.quantidade_entregue
                saldo.save(update_fields=["quantidade", "atualizado_em"])
