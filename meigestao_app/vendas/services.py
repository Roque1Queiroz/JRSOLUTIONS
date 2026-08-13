from django.core.exceptions import ValidationError
from django.db import transaction

from meigestao_app.estoque.models import Estoque, MovimentacaoEstoque
from meigestao_app.vendas.models import ItemVenda, Venda


@transaction.atomic
def confirmar_venda(venda_id: int) -> Venda:
    venda = Venda.objects.select_for_update().get(pk=venda_id)
    itens = list(
        ItemVenda.objects.select_for_update()
        .filter(venda=venda)
        .order_by('produto_vinculado_id', 'pk')
    )
    itens_controlados = [item for item in itens if item.produto_vinculado_id]

    if venda.status == 'confirmada':
        movimentos = {
            movimento.item_venda_id: movimento
            for movimento in MovimentacaoEstoque.objects.filter(
                item_venda__in=itens_controlados
            )
        }
        if all(
            (movimento := movimentos.get(item.pk)) is not None
            and movimento.empresa_id == venda.empresa_id
            and movimento.produto_id == item.produto_vinculado_id
            and movimento.tipo_movimento == 'saida'
            and movimento.quantidade == item.quantidade
            for item in itens_controlados
        ):
            return venda
        raise ValidationError(
            'A venda já está confirmada, mas seus efeitos de estoque estão incompletos.'
        )

    if venda.status != 'rascunho':
        raise ValidationError('Somente uma venda em rascunho pode ser confirmada.')

    produto_ids = sorted({item.produto_vinculado_id for item in itens_controlados})
    estoques = {
        estoque.produto_id: estoque
        for estoque in Estoque.objects.select_for_update()
        .filter(produto_id__in=produto_ids)
        .order_by('produto_id')
    }

    necessidade_por_produto = {}
    nome_por_produto = {}
    for item in itens_controlados:
        produto_id = item.produto_vinculado_id
        necessidade_por_produto[produto_id] = (
            necessidade_por_produto.get(produto_id, 0) + item.quantidade
        )
        nome_por_produto.setdefault(produto_id, item.produto_nome)

    for produto_id, necessario in necessidade_por_produto.items():
        estoque = estoques.get(produto_id)
        disponivel = estoque.quantidade if estoque else 0
        if disponivel < necessario:
            raise ValidationError(
                {
                    'itens': (
                        f'Estoque insuficiente para {nome_por_produto[produto_id]}. '
                        f'Disponível: {disponivel}; necessário: {necessario}.'
                    )
                }
            )

    for item in itens_controlados:
        MovimentacaoEstoque.objects.create(
            item_venda=item,
            empresa=venda.empresa,
            produto=item.produto_vinculado,
            tipo_movimento='saida',
            quantidade=item.quantidade,
            motivo=f'Confirmação da venda #{venda.pk}',
        )

    venda.status = 'confirmada'
    venda.save(update_fields=['status', 'atualizado_em'])
    return venda
