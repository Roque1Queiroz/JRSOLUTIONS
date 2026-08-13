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


@transaction.atomic
def cancelar_venda(venda_id: int) -> Venda:
    from meigestao_app.financeiro.models import Transacao

    venda = Venda.objects.select_for_update().get(pk=venda_id)
    from meigestao_app.fiscal.models import NotaFiscal

    notas_fiscais = list(
        NotaFiscal.objects.select_for_update().filter(venda=venda).order_by('pk')
    )
    if any(nota.status == 'emitida' for nota in notas_fiscais):
        raise ValidationError(
            'Cancele a nota fiscal emitida antes de cancelar a venda.'
        )

    transacoes = list(
        Transacao.objects.select_for_update().filter(venda=venda).order_by('pk')
    )
    if any(transacao.paga for transacao in transacoes):
        raise ValidationError(
            'A venda possui uma transação paga. Estorne a transação antes de cancelá-la.'
        )

    itens = list(
        ItemVenda.objects.select_for_update()
        .filter(venda=venda)
        .order_by('produto_vinculado_id', 'pk')
    )
    itens_controlados = [item for item in itens if item.produto_vinculado_id]
    saidas = list(
        MovimentacaoEstoque.objects.select_for_update()
        .filter(item_venda__in=itens_controlados)
        .order_by('produto_id', 'pk')
    )
    saidas_por_item = {saida.item_venda_id: saida for saida in saidas}

    if venda.status == 'cancelada':
        if transacoes:
            raise ValidationError(
                'A venda já está cancelada, mas ainda possui uma transação financeira vinculada.'
            )
        if all(
            (saida := saidas_por_item.get(item.pk)) is not None
            and hasattr(saida, 'movimento_devolucao_estoque')
            and saida.movimento_devolucao_estoque.empresa_id == venda.empresa_id
            and saida.movimento_devolucao_estoque.produto_id
            == item.produto_vinculado_id
            and saida.movimento_devolucao_estoque.tipo_movimento == 'devolucao'
            and saida.movimento_devolucao_estoque.quantidade == item.quantidade
            for item in itens_controlados
        ):
            return venda
        raise ValidationError(
            'A venda já está cancelada, mas suas devoluções de estoque estão incompletas.'
        )

    if venda.status != 'confirmada':
        raise ValidationError('Somente uma venda confirmada pode ser cancelada.')

    if len(saidas_por_item) != len(itens_controlados) or any(
        (saida := saidas_por_item.get(item.pk)) is None
        or saida.empresa_id != venda.empresa_id
        or saida.produto_id != item.produto_vinculado_id
        or saida.tipo_movimento != 'saida'
        or saida.quantidade != item.quantidade
        for item in itens_controlados
    ):
        raise ValidationError(
            'A venda não pode ser cancelada porque sua baixa de estoque está incoerente.'
        )

    produto_ids = sorted({saida.produto_id for saida in saidas})
    estoques = list(
        Estoque.objects.select_for_update()
        .filter(produto_id__in=produto_ids)
        .order_by('produto_id')
    )
    if {estoque.produto_id for estoque in estoques} != set(produto_ids):
        raise ValidationError(
            'A venda não pode ser cancelada porque falta uma linha de estoque.'
        )

    for item in itens_controlados:
        saida = saidas_por_item[item.pk]
        MovimentacaoEstoque.objects.create(
            movimento_saida_estornado=saida,
            empresa=venda.empresa,
            produto_id=saida.produto_id,
            tipo_movimento='devolucao',
            quantidade=saida.quantidade,
            motivo=f'Cancelamento da venda #{venda.pk}',
        )

    for transacao in transacoes:
        transacao.delete()

    venda.status = 'cancelada'
    venda.save(update_fields=['status', 'atualizado_em'])
    return venda
