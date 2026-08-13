from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import DatabaseError, transaction
from django.utils import timezone
from django.urls import reverse
from meigestao_app.vendas.forms import ItemVendaForm, VendaForm
from meigestao_app.vendas.models import Venda, ItemVenda
from meigestao_app.clientes.models import Cliente
from meigestao_app.core.models import Empresa
from meigestao_app.usuarios.models import Perfil

@pytest.fixture
def setup_data(db):
    empresa = Empresa.objects.create(nome="Empresa Teste", cnpj="12.345.678/0001-99")
    cliente = Cliente.objects.create(
        empresa=empresa,
        nome="Cliente Teste",
        cpf_cnpj="123.456.789-00",
        email="teste@teste.com",
    )
    return empresa, cliente

@pytest.mark.django_db
class TestVendaFlow:
    """Testa o ciclo de vida básico de uma venda."""

    def test_confirmar_venda_baixa_estoque_uma_unica_vez(self, setup_data):
        from meigestao_app.estoque.models import (
            Categoria,
            Estoque,
            MovimentacaoEstoque,
            Produto,
        )
        from meigestao_app.vendas.services import confirmar_venda

        empresa, cliente = setup_data
        categoria = Categoria.objects.create(
            empresa=empresa,
            nome='Categoria confirmação',
        )
        produto = Produto.objects.create(
            empresa=empresa,
            categoria=categoria,
            nome='Produto confirmação idempotente',
            sku='VENDA-CONF-001',
            preco_custo=Decimal('10.00'),
            preco_venda=Decimal('20.00'),
        )
        estoque = Estoque.objects.create(
            empresa=empresa,
            produto=produto,
            quantidade=10,
        )
        venda = Venda.objects.create(
            empresa=empresa,
            cliente=cliente,
            status='rascunho',
        )
        item = ItemVenda.objects.create(
            venda=venda,
            produto_vinculado=produto,
            produto_nome=produto.nome,
            quantidade=3,
            preco_unitario=Decimal('20.00'),
        )

        confirmar_venda(venda.pk)
        confirmar_venda(venda.pk)

        venda.refresh_from_db()
        estoque.refresh_from_db()
        movimentos = MovimentacaoEstoque.objects.filter(item_venda=item)
        assert venda.status == 'confirmada'
        assert estoque.quantidade == 7
        assert movimentos.count() == 1
        assert movimentos.get().tipo_movimento == 'saida'
        assert movimentos.get().quantidade == 3

    def test_confirmar_venda_rejeita_soma_de_itens_sem_estoque_e_reverte_tudo(
        self, setup_data
    ):
        from meigestao_app.estoque.models import (
            Categoria,
            Estoque,
            MovimentacaoEstoque,
            Produto,
        )
        from meigestao_app.financeiro.models import Transacao
        from meigestao_app.vendas.services import confirmar_venda

        empresa, cliente = setup_data
        categoria = Categoria.objects.create(empresa=empresa, nome='Categoria insuficiente')
        produto = Produto.objects.create(
            empresa=empresa,
            categoria=categoria,
            nome='Produto insuficiente',
            sku='VENDA-INSUF-001',
            preco_custo=Decimal('10.00'),
            preco_venda=Decimal('20.00'),
        )
        estoque = Estoque.objects.create(
            empresa=empresa,
            produto=produto,
            quantidade=5,
        )
        venda = Venda.objects.create(
            empresa=empresa,
            cliente=cliente,
            status='rascunho',
        )
        ItemVenda.objects.create(
            venda=venda,
            produto_vinculado=produto,
            produto_nome=produto.nome,
            quantidade=3,
            preco_unitario=Decimal('20.00'),
        )
        ItemVenda.objects.create(
            venda=venda,
            produto_vinculado=produto,
            produto_nome=produto.nome,
            quantidade=3,
            preco_unitario=Decimal('20.00'),
        )

        with pytest.raises(ValidationError):
            confirmar_venda(venda.pk)

        venda.refresh_from_db()
        estoque.refresh_from_db()
        assert venda.status == 'rascunho'
        assert estoque.quantidade == 5
        assert not MovimentacaoEstoque.objects.filter(item_venda__venda=venda).exists()
        assert not Transacao.objects.filter(venda=venda).exists()

    def test_post_de_edicao_confirma_venda_pelo_servico_e_baixa_estoque(
        self, client, setup_data
    ):
        from datetime import date
        from meigestao_app.estoque.models import (
            Categoria,
            Estoque,
            MovimentacaoEstoque,
            Produto,
        )

        empresa, cliente_venda = setup_data
        usuario = User.objects.create_user(username='vendedor_confirmacao', password='senha')
        Perfil.objects.create(
            usuario=usuario,
            empresa=empresa,
            permissao='vendedor',
            data_admissao=date.today(),
        )
        categoria = Categoria.objects.create(empresa=empresa, nome='Categoria HTTP')
        produto = Produto.objects.create(
            empresa=empresa,
            categoria=categoria,
            nome='Produto confirmação HTTP',
            sku='VENDA-HTTP-001',
            preco_custo=Decimal('10.00'),
            preco_venda=Decimal('25.00'),
        )
        estoque = Estoque.objects.create(
            empresa=empresa,
            produto=produto,
            quantidade=8,
        )
        venda = Venda.objects.create(
            empresa=empresa,
            cliente=cliente_venda,
            status='rascunho',
        )
        item = ItemVenda.objects.create(
            venda=venda,
            produto_vinculado=produto,
            produto_nome=produto.nome,
            quantidade=2,
            preco_unitario=Decimal('25.00'),
        )
        client.force_login(usuario)

        response = client.post(
            reverse('vendas:venda_update', kwargs={'pk': venda.pk}),
            {
                'cliente': cliente_venda.pk,
                'data_venda': venda.data_venda.strftime('%Y-%m-%dT%H:%M'),
                'descricao': venda.descricao,
                'desconto': '0.00',
                'status': 'confirmada',
                'observacoes': venda.observacoes,
                'itens-TOTAL_FORMS': '1',
                'itens-INITIAL_FORMS': '1',
                'itens-MIN_NUM_FORMS': '0',
                'itens-MAX_NUM_FORMS': '1000',
                'itens-0-id': item.pk,
                'itens-0-venda': venda.pk,
                'itens-0-produto_vinculado': produto.pk,
                'itens-0-produto_nome': produto.nome,
                'itens-0-quantidade': '2',
                'itens-0-preco_unitario': '25.00',
            },
        )

        venda.refresh_from_db()
        estoque.refresh_from_db()
        assert response.status_code == 302
        assert venda.status == 'confirmada'
        assert estoque.quantidade == 6
        assert MovimentacaoEstoque.objects.filter(item_venda=item).count() == 1

    def test_post_de_criacao_confirmada_baixa_estoque_pelo_servico(
        self, client, setup_data
    ):
        from datetime import date
        from meigestao_app.estoque.models import Categoria, Estoque, MovimentacaoEstoque, Produto

        empresa, cliente_venda = setup_data
        usuario = User.objects.create_user(username='vendedor_criacao', password='senha')
        Perfil.objects.create(
            usuario=usuario,
            empresa=empresa,
            permissao='vendedor',
            data_admissao=date.today(),
        )
        categoria = Categoria.objects.create(empresa=empresa, nome='Categoria criação HTTP')
        produto = Produto.objects.create(
            empresa=empresa,
            categoria=categoria,
            nome='Produto criação confirmada',
            sku='VENDA-CREATE-001',
            preco_custo=Decimal('10.00'),
            preco_venda=Decimal('30.00'),
        )
        estoque = Estoque.objects.create(
            empresa=empresa,
            produto=produto,
            quantidade=9,
        )
        client.force_login(usuario)

        response = client.post(
            reverse('vendas:venda_create'),
            {
                'cliente': cliente_venda.pk,
                'data_venda': timezone.now().strftime('%Y-%m-%dT%H:%M'),
                'descricao': '',
                'desconto': '0.00',
                'status': 'confirmada',
                'observacoes': '',
                'itens-TOTAL_FORMS': '1',
                'itens-INITIAL_FORMS': '0',
                'itens-MIN_NUM_FORMS': '0',
                'itens-MAX_NUM_FORMS': '1000',
                'itens-0-produto_vinculado': produto.pk,
                'itens-0-produto_nome': produto.nome,
                'itens-0-quantidade': '2',
                'itens-0-preco_unitario': '30.00',
            },
        )

        venda = Venda.objects.get(empresa=empresa, cliente=cliente_venda)
        item = venda.itens.get()
        estoque.refresh_from_db()
        assert response.status_code == 302
        assert venda.status == 'confirmada'
        assert estoque.quantidade == 7
        assert MovimentacaoEstoque.objects.filter(item_venda=item).count() == 1

    def test_queryset_nao_confirma_venda_sem_baixa_de_estoque(self, setup_data):
        from meigestao_app.estoque.models import Categoria, Estoque, Produto

        empresa, cliente = setup_data
        categoria = Categoria.objects.create(empresa=empresa, nome='Categoria bypass ORM')
        produto = Produto.objects.create(
            empresa=empresa,
            categoria=categoria,
            nome='Produto bypass ORM',
            sku='VENDA-ORM-001',
            preco_custo=Decimal('10.00'),
            preco_venda=Decimal('20.00'),
        )
        estoque = Estoque.objects.create(empresa=empresa, produto=produto, quantidade=6)
        venda = Venda.objects.create(empresa=empresa, cliente=cliente, status='rascunho')
        ItemVenda.objects.create(
            venda=venda,
            produto_vinculado=produto,
            produto_nome=produto.nome,
            quantidade=2,
            preco_unitario=Decimal('20.00'),
        )

        with pytest.raises(DatabaseError):
            with transaction.atomic():
                Venda.objects.filter(pk=venda.pk).update(status='confirmada')

        venda.refresh_from_db()
        estoque.refresh_from_db()
        assert venda.status == 'rascunho'
        assert estoque.quantidade == 6

    def test_editar_movimento_de_venda_nao_reaplica_baixa(self, setup_data):
        from meigestao_app.estoque.models import Categoria, Estoque, Produto
        from meigestao_app.vendas.services import confirmar_venda

        empresa, cliente = setup_data
        categoria = Categoria.objects.create(empresa=empresa, nome='Categoria movimento')
        produto = Produto.objects.create(
            empresa=empresa,
            categoria=categoria,
            nome='Produto movimento imutável',
            sku='VENDA-MOV-001',
            preco_custo=Decimal('10.00'),
            preco_venda=Decimal('20.00'),
        )
        estoque = Estoque.objects.create(empresa=empresa, produto=produto, quantidade=7)
        venda = Venda.objects.create(empresa=empresa, cliente=cliente, status='rascunho')
        item = ItemVenda.objects.create(
            venda=venda,
            produto_vinculado=produto,
            produto_nome=produto.nome,
            quantidade=2,
            preco_unitario=Decimal('20.00'),
        )
        confirmar_venda(venda.pk)
        movimento = item.movimento_saida_estoque
        movimento.motivo = 'Tentativa de edição'

        movimento.save(update_fields=['motivo', 'atualizado_em'])

        estoque.refresh_from_db()
        assert estoque.quantidade == 5

    def test_item_com_baixa_de_estoque_nao_pode_alterar_quantidade(self, setup_data):
        from meigestao_app.estoque.models import Categoria, Estoque, Produto
        from meigestao_app.vendas.services import confirmar_venda

        empresa, cliente = setup_data
        categoria = Categoria.objects.create(empresa=empresa, nome='Categoria item baixado')
        produto = Produto.objects.create(
            empresa=empresa,
            categoria=categoria,
            nome='Produto item baixado',
            sku='VENDA-ITEM-001',
            preco_custo=Decimal('10.00'),
            preco_venda=Decimal('20.00'),
        )
        estoque = Estoque.objects.create(empresa=empresa, produto=produto, quantidade=8)
        venda = Venda.objects.create(empresa=empresa, cliente=cliente, status='rascunho')
        item = ItemVenda.objects.create(
            venda=venda,
            produto_vinculado=produto,
            produto_nome=produto.nome,
            quantidade=2,
            preco_unitario=Decimal('20.00'),
        )
        confirmar_venda(venda.pk)
        item.quantidade = 3

        with pytest.raises(ValidationError):
            item.save(update_fields=['quantidade'])

        item.refresh_from_db()
        estoque.refresh_from_db()
        assert item.quantidade == 2
        assert estoque.quantidade == 6

    def test_movimento_de_venda_nao_pode_alterar_campos_economicos(self, setup_data):
        from meigestao_app.estoque.models import Categoria, Estoque, Produto
        from meigestao_app.vendas.services import confirmar_venda

        empresa, cliente = setup_data
        categoria = Categoria.objects.create(empresa=empresa, nome='Categoria movimento protegido')
        produto = Produto.objects.create(
            empresa=empresa,
            categoria=categoria,
            nome='Produto movimento protegido',
            sku='VENDA-MOV-PROT-001',
            preco_custo=Decimal('10.00'),
            preco_venda=Decimal('20.00'),
        )
        Estoque.objects.create(empresa=empresa, produto=produto, quantidade=8)
        venda = Venda.objects.create(empresa=empresa, cliente=cliente, status='rascunho')
        item = ItemVenda.objects.create(
            venda=venda,
            produto_vinculado=produto,
            produto_nome=produto.nome,
            quantidade=2,
            preco_unitario=Decimal('20.00'),
        )
        confirmar_venda(venda.pk)
        movimento = item.movimento_saida_estoque
        movimento.quantidade = 5

        with pytest.raises(ValidationError):
            movimento.save(update_fields=['quantidade'])

        movimento.refresh_from_db()
        assert movimento.quantidade == 2
        assert movimento.tipo_movimento == 'saida'
        assert movimento.produto_id == produto.pk

    def test_queryset_nao_altera_item_com_baixa_de_estoque(self, setup_data):
        from meigestao_app.estoque.models import Categoria, Estoque, Produto
        from meigestao_app.vendas.services import confirmar_venda

        empresa, cliente = setup_data
        categoria = Categoria.objects.create(empresa=empresa, nome='Categoria item ORM')
        produto = Produto.objects.create(
            empresa=empresa,
            categoria=categoria,
            nome='Produto item ORM',
            sku='VENDA-ITEM-ORM-001',
            preco_custo=Decimal('10.00'),
            preco_venda=Decimal('20.00'),
        )
        Estoque.objects.create(empresa=empresa, produto=produto, quantidade=8)
        venda = Venda.objects.create(empresa=empresa, cliente=cliente, status='rascunho')
        item = ItemVenda.objects.create(
            venda=venda,
            produto_vinculado=produto,
            produto_nome=produto.nome,
            quantidade=2,
            preco_unitario=Decimal('20.00'),
        )
        confirmar_venda(venda.pk)

        with pytest.raises(DatabaseError):
            with transaction.atomic():
                ItemVenda.objects.filter(pk=item.pk).update(quantidade=3)

        item.refresh_from_db()
        assert item.quantidade == 2

    def test_queryset_nao_altera_movimento_economico_de_venda(self, setup_data):
        from meigestao_app.estoque.models import Categoria, Estoque, MovimentacaoEstoque, Produto
        from meigestao_app.vendas.services import confirmar_venda

        empresa, cliente = setup_data
        categoria = Categoria.objects.create(empresa=empresa, nome='Categoria movimento ORM')
        produto = Produto.objects.create(
            empresa=empresa,
            categoria=categoria,
            nome='Produto movimento ORM',
            sku='VENDA-MOV-ORM-001',
            preco_custo=Decimal('10.00'),
            preco_venda=Decimal('20.00'),
        )
        Estoque.objects.create(empresa=empresa, produto=produto, quantidade=8)
        venda = Venda.objects.create(empresa=empresa, cliente=cliente, status='rascunho')
        item = ItemVenda.objects.create(
            venda=venda,
            produto_vinculado=produto,
            produto_nome=produto.nome,
            quantidade=2,
            preco_unitario=Decimal('20.00'),
        )
        confirmar_venda(venda.pk)
        movimento = item.movimento_saida_estoque

        with pytest.raises(DatabaseError):
            with transaction.atomic():
                MovimentacaoEstoque.objects.filter(pk=movimento.pk).update(quantidade=5)

        movimento.refresh_from_db()
        assert movimento.quantidade == 2

    def test_queryset_nao_exclui_movimento_de_saida_da_venda(self, setup_data):
        from meigestao_app.estoque.models import Categoria, Estoque, MovimentacaoEstoque, Produto
        from meigestao_app.vendas.services import confirmar_venda

        empresa, cliente = setup_data
        categoria = Categoria.objects.create(empresa=empresa, nome='Categoria excluir movimento')
        produto = Produto.objects.create(
            empresa=empresa,
            categoria=categoria,
            nome='Produto excluir movimento',
            sku='VENDA-MOV-DEL-001',
            preco_custo=Decimal('10.00'),
            preco_venda=Decimal('20.00'),
        )
        estoque = Estoque.objects.create(empresa=empresa, produto=produto, quantidade=8)
        venda = Venda.objects.create(empresa=empresa, cliente=cliente, status='rascunho')
        item = ItemVenda.objects.create(
            venda=venda,
            produto_vinculado=produto,
            produto_nome=produto.nome,
            quantidade=2,
            preco_unitario=Decimal('20.00'),
        )
        confirmar_venda(venda.pk)
        movimento = item.movimento_saida_estoque

        with pytest.raises(DatabaseError):
            with transaction.atomic():
                MovimentacaoEstoque.objects.filter(pk=movimento.pk).delete()

        estoque.refresh_from_db()
        assert MovimentacaoEstoque.objects.filter(pk=movimento.pk).exists()
        assert estoque.quantidade == 6

    def test_nao_adiciona_produto_controlado_a_venda_ja_confirmada(self, setup_data):
        from meigestao_app.estoque.models import Categoria, Estoque, Produto

        empresa, cliente = setup_data
        categoria = Categoria.objects.create(empresa=empresa, nome='Categoria inserção ativa')
        produto = Produto.objects.create(
            empresa=empresa,
            categoria=categoria,
            nome='Produto inserção ativa',
            sku='VENDA-INSERT-ATIVA-001',
            preco_custo=Decimal('10.00'),
            preco_venda=Decimal('20.00'),
        )
        Estoque.objects.create(empresa=empresa, produto=produto, quantidade=8)
        venda = Venda.objects.create(
            empresa=empresa,
            cliente=cliente,
            status='confirmada',
        )

        with pytest.raises(ValidationError):
            ItemVenda.objects.create(
                venda=venda,
                produto_vinculado=produto,
                produto_nome=produto.nome,
                quantidade=2,
                preco_unitario=Decimal('20.00'),
            )

        assert not venda.itens.exists()

    def test_bulk_create_nao_adiciona_produto_controlado_a_venda_ativa(self, setup_data):
        from meigestao_app.estoque.models import Categoria, Estoque, Produto

        empresa, cliente = setup_data
        categoria = Categoria.objects.create(empresa=empresa, nome='Categoria bulk ativa')
        produto = Produto.objects.create(
            empresa=empresa,
            categoria=categoria,
            nome='Produto bulk ativo',
            sku='VENDA-BULK-ATIVA-001',
            preco_custo=Decimal('10.00'),
            preco_venda=Decimal('20.00'),
        )
        Estoque.objects.create(empresa=empresa, produto=produto, quantidade=8)
        venda = Venda.objects.create(
            empresa=empresa,
            cliente=cliente,
            status='confirmada',
        )

        with pytest.raises(DatabaseError):
            with transaction.atomic():
                ItemVenda.objects.bulk_create([
                    ItemVenda(
                        venda=venda,
                        produto_vinculado=produto,
                        produto_nome=produto.nome,
                        quantidade=2,
                        preco_unitario=Decimal('20.00'),
                        subtotal=Decimal('40.00'),
                    )
                ])

        assert not venda.itens.exists()

    def test_item_existente_nao_ganha_produto_controlado_em_venda_ativa(self, setup_data):
        from meigestao_app.estoque.models import Categoria, Estoque, Produto

        empresa, cliente = setup_data
        categoria = Categoria.objects.create(empresa=empresa, nome='Categoria controle posterior')
        produto = Produto.objects.create(
            empresa=empresa,
            categoria=categoria,
            nome='Produto controle posterior',
            sku='VENDA-CONTROLE-POST-001',
            preco_custo=Decimal('10.00'),
            preco_venda=Decimal('20.00'),
        )
        Estoque.objects.create(empresa=empresa, produto=produto, quantidade=8)
        venda = Venda.objects.create(empresa=empresa, cliente=cliente, status='confirmada')
        item = ItemVenda.objects.create(
            venda=venda,
            produto_nome='Serviço sem estoque',
            quantidade=1,
            preco_unitario=Decimal('20.00'),
        )
        item.produto_vinculado = produto

        with pytest.raises(ValidationError):
            item.save(update_fields=['produto_vinculado'])

        item.refresh_from_db()
        assert item.produto_vinculado_id is None

    def test_queryset_nao_introduz_produto_controlado_em_venda_ativa(self, setup_data):
        from meigestao_app.estoque.models import Categoria, Estoque, Produto

        empresa, cliente = setup_data
        categoria = Categoria.objects.create(empresa=empresa, nome='Categoria controle ORM')
        produto = Produto.objects.create(
            empresa=empresa,
            categoria=categoria,
            nome='Produto controle ORM',
            sku='VENDA-CONTROLE-ORM-001',
            preco_custo=Decimal('10.00'),
            preco_venda=Decimal('20.00'),
        )
        Estoque.objects.create(empresa=empresa, produto=produto, quantidade=8)
        venda = Venda.objects.create(empresa=empresa, cliente=cliente, status='confirmada')
        item = ItemVenda.objects.create(
            venda=venda,
            produto_nome='Serviço ORM',
            quantidade=1,
            preco_unitario=Decimal('20.00'),
        )

        with pytest.raises(DatabaseError):
            with transaction.atomic():
                ItemVenda.objects.filter(pk=item.pk).update(produto_vinculado=produto)

        item.refresh_from_db()
        assert item.produto_vinculado_id is None

    def test_bulk_create_movimento_vinculado_aplica_baixa_real(self, setup_data):
        from meigestao_app.estoque.models import Categoria, Estoque, MovimentacaoEstoque, Produto

        empresa, cliente = setup_data
        categoria = Categoria.objects.create(empresa=empresa, nome='Categoria movimento bulk')
        produto = Produto.objects.create(
            empresa=empresa,
            categoria=categoria,
            nome='Produto movimento bulk',
            sku='VENDA-MOV-BULK-001',
            preco_custo=Decimal('10.00'),
            preco_venda=Decimal('20.00'),
        )
        estoque = Estoque.objects.create(empresa=empresa, produto=produto, quantidade=8)
        venda = Venda.objects.create(empresa=empresa, cliente=cliente, status='rascunho')
        item = ItemVenda.objects.create(
            venda=venda,
            produto_vinculado=produto,
            produto_nome=produto.nome,
            quantidade=3,
            preco_unitario=Decimal('20.00'),
        )

        MovimentacaoEstoque.objects.bulk_create([
            MovimentacaoEstoque(
                item_venda=item,
                empresa=empresa,
                produto=produto,
                tipo_movimento='saida',
                quantidade=3,
                motivo='Baixa via bulk segura',
            )
        ])
        Venda.objects.filter(pk=venda.pk).update(status='confirmada')

        estoque.refresh_from_db()
        venda.refresh_from_db()
        assert estoque.quantidade == 5
        assert venda.status == 'confirmada'
        assert MovimentacaoEstoque.objects.filter(item_venda=item).count() == 1

    def test_bulk_create_rejeita_movimento_vinculado_divergente_sem_baixa(self, setup_data):
        from meigestao_app.estoque.models import Categoria, Estoque, MovimentacaoEstoque, Produto

        empresa, cliente = setup_data
        categoria = Categoria.objects.create(empresa=empresa, nome='Categoria movimento forjado')
        produto = Produto.objects.create(
            empresa=empresa,
            categoria=categoria,
            nome='Produto movimento forjado',
            sku='VENDA-MOV-FORJADO-001',
            preco_custo=Decimal('10.00'),
            preco_venda=Decimal('20.00'),
        )
        estoque = Estoque.objects.create(empresa=empresa, produto=produto, quantidade=8)
        venda = Venda.objects.create(empresa=empresa, cliente=cliente, status='rascunho')
        item = ItemVenda.objects.create(
            venda=venda,
            produto_vinculado=produto,
            produto_nome=produto.nome,
            quantidade=3,
            preco_unitario=Decimal('20.00'),
        )

        with pytest.raises(DatabaseError):
            with transaction.atomic():
                MovimentacaoEstoque.objects.bulk_create([
                    MovimentacaoEstoque(
                        item_venda=item,
                        empresa=empresa,
                        produto=produto,
                        tipo_movimento='saida',
                        quantidade=1,
                        motivo='Movimento forjado',
                    )
                ])

        estoque.refresh_from_db()
        venda.refresh_from_db()
        assert estoque.quantidade == 8
        assert venda.status == 'rascunho'
        assert not MovimentacaoEstoque.objects.filter(item_venda=item).exists()

    def test_movimento_avulso_nao_pode_receber_vinculo_posterior_por_save(self, setup_data):
        from meigestao_app.estoque.models import Categoria, Estoque, MovimentacaoEstoque, Produto

        empresa, cliente = setup_data
        categoria = Categoria.objects.create(empresa=empresa, nome='Categoria vínculo save')
        produto = Produto.objects.create(
            empresa=empresa, categoria=categoria, nome='Produto vínculo save',
            sku='VENDA-VINC-SAVE-001', preco_custo=Decimal('10.00'), preco_venda=Decimal('20.00'),
        )
        Estoque.objects.create(empresa=empresa, produto=produto, quantidade=8)
        venda = Venda.objects.create(empresa=empresa, cliente=cliente, status='rascunho')
        item = ItemVenda.objects.create(
            venda=venda, produto_vinculado=produto, produto_nome=produto.nome,
            quantidade=3, preco_unitario=Decimal('20.00'),
        )
        movimento = MovimentacaoEstoque.objects.create(
            empresa=empresa, produto=produto, tipo_movimento='saida',
            quantidade=3, motivo='Movimento avulso',
        )
        movimento.item_venda = item

        with pytest.raises(ValidationError):
            movimento.save(update_fields=['item_venda'])

        movimento.refresh_from_db()
        assert movimento.item_venda_id is None

    @pytest.mark.parametrize('metodo', ['update', 'bulk_update'])
    def test_movimento_avulso_nao_pode_receber_vinculo_posterior_em_lote(
        self, setup_data, metodo
    ):
        from meigestao_app.estoque.models import Categoria, Estoque, MovimentacaoEstoque, Produto

        empresa, cliente = setup_data
        categoria = Categoria.objects.create(empresa=empresa, nome=f'Categoria vínculo {metodo}')
        produto = Produto.objects.create(
            empresa=empresa, categoria=categoria, nome=f'Produto vínculo {metodo}',
            sku=f'VENDA-VINC-{metodo.upper()}-001',
            preco_custo=Decimal('10.00'), preco_venda=Decimal('20.00'),
        )
        estoque = Estoque.objects.create(empresa=empresa, produto=produto, quantidade=8)
        venda = Venda.objects.create(empresa=empresa, cliente=cliente, status='rascunho')
        item = ItemVenda.objects.create(
            venda=venda, produto_vinculado=produto, produto_nome=produto.nome,
            quantidade=3, preco_unitario=Decimal('20.00'),
        )
        movimento = MovimentacaoEstoque.objects.bulk_create([
            MovimentacaoEstoque(
                empresa=empresa, produto=produto, tipo_movimento='saida',
                quantidade=3, motivo='Movimento avulso em lote',
            )
        ])[0]

        with pytest.raises(DatabaseError):
            with transaction.atomic():
                if metodo == 'update':
                    MovimentacaoEstoque.objects.filter(pk=movimento.pk).update(item_venda=item)
                else:
                    movimento.item_venda = item
                    MovimentacaoEstoque.objects.bulk_update([movimento], ['item_venda'])

        movimento.refresh_from_db()
        estoque.refresh_from_db()
        venda.refresh_from_db()
        assert movimento.item_venda_id is None
        assert estoque.quantidade == 8
        assert venda.status == 'rascunho'

    def test_trigger_postgresql_bloqueia_venda_item_e_estoque_nessa_ordem(self):
        import importlib
        import re

        migracao = importlib.import_module(
            'meigestao_app.vendas.migrations.0005_exigir_baixa_estoque_confirmacao'
        )
        sql = migracao.POSTGRES_FUNCTION

        def posicao_lock(tabela, predicado, sufixo='FOR UPDATE'):
            padrao = rf'FROM {tabela}\s+WHERE {predicado}\s+{sufixo}'
            encontrado = re.search(padrao, sql)
            assert encontrado, f'Lock {sufixo} ausente em {tabela}.'
            return encontrado.start()

        lock_venda = posicao_lock('vendas_venda', r'id = venda_id_inicial')
        lock_item = posicao_lock(
            'vendas_itemvenda', r'id = NEW\.item_venda_id', 'FOR UPDATE NOWAIT'
        )
        lock_estoque = posicao_lock('estoque_estoque', r'produto_id = NEW\.produto_id')

        assert lock_venda < lock_item < lock_estoque

    def test_venda_creation_logic(self, setup_data):
        empresa, cliente = setup_data
        
        # Criar Venda
        venda = Venda.objects.create(
            empresa=empresa,
            cliente=cliente,
            status='confirmada'
        )
        
        # Adicionar Itens
        ItemVenda.objects.create(
            venda=venda,
            produto_nome="Produto A",
            quantidade=2,
            preco_unitario=50.00
        )
        ItemVenda.objects.create(
            venda=venda,
            produto_nome="Produto B",
            quantidade=1,
            preco_unitario=150.00
        )
        
        # Validar Cálculos
        total = venda.calcular_total()
        venda.save()
        
        assert total == 250.00
        assert venda.valor_total == 250.00
        assert venda.itens.count() == 2

    def test_tela_criacao_venda_filtra_cliente_e_produto_por_empresa(self, client, db):
        from datetime import date
        from meigestao_app.estoque.models import Categoria, Produto

        empresa_a = Empresa.objects.create(nome="Empresa A", cnpj="11.111.111/0001-11")
        empresa_b = Empresa.objects.create(nome="Empresa B", cnpj="22.222.222/0001-22")
        usuario_a = User.objects.create_user(username="vendedor_a", password="senha")
        Perfil.objects.create(
            usuario=usuario_a,
            empresa=empresa_a,
            permissao="vendedor",
            data_admissao=date.today(),
        )
        cliente_a = Cliente.objects.create(
            empresa=empresa_a,
            nome="Cliente A",
            cpf_cnpj="123.456.789-00",
        )
        cliente_b = Cliente.objects.create(
            empresa=empresa_b,
            nome="Cliente B",
            cpf_cnpj="987.654.321-00",
        )
        categoria_a = Categoria.objects.create(empresa=empresa_a, nome="Categoria A")
        categoria_b = Categoria.objects.create(empresa=empresa_b, nome="Categoria B")
        produto_a = Produto.objects.create(
            empresa=empresa_a,
            categoria=categoria_a,
            nome="Produto A",
            sku="PROD-A-VIEW",
            preco_custo="10.00",
            preco_venda="20.00",
        )
        produto_b = Produto.objects.create(
            empresa=empresa_b,
            categoria=categoria_b,
            nome="Produto B",
            sku="PROD-B-VIEW",
            preco_custo="10.00",
            preco_venda="20.00",
        )
        client.force_login(usuario_a)

        response = client.get(reverse("vendas:venda_create"))

        assert response.status_code == 200
        assert list(response.context["form"].fields["cliente"].queryset) == [cliente_a]
        produto_queryset = response.context["formset"].forms[0].fields["produto_vinculado"].queryset
        assert list(produto_queryset) == [produto_a]
        assert cliente_b not in response.context["form"].fields["cliente"].queryset
        assert produto_b not in produto_queryset

    def test_formulario_venda_rejeita_cliente_de_outra_empresa(self, db):
        empresa_a = Empresa.objects.create(nome="Empresa A", cnpj="11.111.111/0001-11")
        empresa_b = Empresa.objects.create(nome="Empresa B", cnpj="22.222.222/0001-22")
        cliente_b = Cliente.objects.create(
            empresa=empresa_b,
            nome="Cliente B",
            cpf_cnpj="987.654.321-00",
        )

        form = VendaForm(
            data={
                "cliente": cliente_b.pk,
                "data_venda": timezone.now().strftime("%Y-%m-%dT%H:%M"),
                "descricao": "",
                "desconto": "0.00",
                "status": "rascunho",
                "observacoes": "",
            },
            empresa=empresa_a,
        )

        assert not form.is_valid()
        assert "cliente" in form.errors

    def test_formulario_item_rejeita_produto_de_outra_empresa(self, db):
        from meigestao_app.estoque.models import Categoria, Produto

        empresa_a = Empresa.objects.create(nome="Empresa A", cnpj="11.111.111/0001-11")
        empresa_b = Empresa.objects.create(nome="Empresa B", cnpj="22.222.222/0001-22")
        categoria_b = Categoria.objects.create(empresa=empresa_b, nome="Categoria B")
        produto_b = Produto.objects.create(
            empresa=empresa_b,
            categoria=categoria_b,
            nome="Produto B",
            sku="PROD-B-FORM",
            preco_custo="10.00",
            preco_venda="20.00",
        )

        form = ItemVendaForm(
            data={
                "produto_vinculado": produto_b.pk,
                "produto_nome": produto_b.nome,
                "quantidade": 1,
                "preco_unitario": "20.00",
            },
            empresa=empresa_a,
        )

        assert not form.is_valid()
        assert "produto_vinculado" in form.errors

    def test_venda_rejeita_cliente_de_outra_empresa_no_modelo(self, db):
        empresa_a = Empresa.objects.create(nome="Empresa A", cnpj="11.111.111/0001-11")
        empresa_b = Empresa.objects.create(nome="Empresa B", cnpj="22.222.222/0001-22")
        cliente_b = Cliente.objects.create(
            empresa=empresa_b,
            nome="Cliente B",
            cpf_cnpj="987.654.321-00",
        )

        venda = Venda(empresa=empresa_a, cliente=cliente_b)

        with pytest.raises(ValidationError):
            venda.save()

        assert not Venda.objects.filter(empresa=empresa_a, cliente=cliente_b).exists()

    def test_venda_rejeita_desconto_negativo_no_modelo(self, setup_data):
        empresa, cliente = setup_data
        venda = Venda(empresa=empresa, cliente=cliente, desconto="-0.01")

        with pytest.raises(ValidationError):
            venda.save()

        assert not Venda.objects.filter(empresa=empresa, cliente=cliente).exists()

    def test_item_venda_rejeita_quantidade_zero_no_modelo(self, setup_data):
        empresa, cliente = setup_data
        venda = Venda.objects.create(empresa=empresa, cliente=cliente)
        item = ItemVenda(
            venda=venda,
            produto_nome="Produto inválido",
            quantidade=0,
            preco_unitario="10.00",
        )

        with pytest.raises(ValidationError):
            item.save()

        assert not ItemVenda.objects.filter(venda=venda).exists()

    def test_item_venda_rejeita_preco_negativo_no_modelo(self, setup_data):
        empresa, cliente = setup_data
        venda = Venda.objects.create(empresa=empresa, cliente=cliente)
        item = ItemVenda(
            venda=venda,
            produto_nome="Produto inválido",
            quantidade=1,
            preco_unitario="-0.01",
        )

        with pytest.raises(ValidationError):
            item.save()

        assert not ItemVenda.objects.filter(venda=venda).exists()

    def test_item_venda_rejeita_produto_de_outra_empresa_no_modelo(self, db):
        from meigestao_app.estoque.models import Categoria, Produto

        empresa_a = Empresa.objects.create(nome="Empresa A", cnpj="11.111.111/0001-11")
        empresa_b = Empresa.objects.create(nome="Empresa B", cnpj="22.222.222/0001-22")
        cliente_a = Cliente.objects.create(
            empresa=empresa_a,
            nome="Cliente A",
            cpf_cnpj="123.456.789-00",
        )
        categoria_b = Categoria.objects.create(empresa=empresa_b, nome="Categoria B")
        produto_b = Produto.objects.create(
            empresa=empresa_b,
            categoria=categoria_b,
            nome="Produto B",
            sku="PROD-B",
            preco_custo="10.00",
            preco_venda="20.00",
        )
        venda_a = Venda.objects.create(empresa=empresa_a, cliente=cliente_a)
        item = ItemVenda(
            venda=venda_a,
            produto_vinculado=produto_b,
            produto_nome=produto_b.nome,
            quantidade=1,
            preco_unitario="20.00",
        )

        with pytest.raises(ValidationError):
            item.save()

        assert not ItemVenda.objects.filter(venda=venda_a, produto_vinculado=produto_b).exists()

    def test_item_de_venda_liquidada_nao_pode_ser_alterado(self, setup_data):
        from meigestao_app.financeiro.models import ContaBancaria

        empresa, cliente = setup_data
        conta = ContaBancaria.objects.create(
            empresa=empresa,
            banco="Banco Teste",
            agencia="0001",
            conta="12345-6",
            saldo=Decimal("0.00"),
        )
        venda = Venda.objects.create(
            empresa=empresa,
            cliente=cliente,
            status="confirmada",
        )
        item = ItemVenda.objects.create(
            venda=venda,
            produto_nome="Produto liquidado",
            quantidade=1,
            preco_unitario=Decimal("100.00"),
        )
        transacao = venda.transacao_financeira
        transacao.conta = conta
        transacao.paga = True
        transacao.save(update_fields=['conta', 'paga', 'atualizado_em'])

        item.preco_unitario = Decimal("150.00")
        with pytest.raises(ValidationError):
            item.save()

        item.refresh_from_db()
        transacao.refresh_from_db()
        conta.refresh_from_db()
        assert item.preco_unitario == Decimal("100.00")
        assert transacao.valor == Decimal("100.00")
        assert conta.saldo == Decimal("100.00")

    def test_venda_liquidada_nao_pode_ser_alterada_diretamente(self, setup_data):
        from meigestao_app.financeiro.models import ContaBancaria

        empresa, cliente = setup_data
        conta = ContaBancaria.objects.create(
            empresa=empresa,
            banco="Banco Venda",
            agencia="0002",
            conta="23456-7",
            saldo=Decimal("0.00"),
        )
        venda = Venda.objects.create(empresa=empresa, cliente=cliente, status="confirmada")
        ItemVenda.objects.create(
            venda=venda,
            produto_nome="Produto venda",
            quantidade=1,
            preco_unitario=Decimal("100.00"),
        )
        transacao = venda.transacao_financeira
        transacao.conta = conta
        transacao.paga = True
        transacao.save(update_fields=['conta', 'paga', 'atualizado_em'])

        venda.desconto = Decimal("20.00")
        with pytest.raises(ValidationError):
            venda.save()

        venda.refresh_from_db()
        transacao.refresh_from_db()
        conta.refresh_from_db()
        assert venda.desconto == Decimal("0.00")
        assert venda.valor_total == Decimal("100.00")
        assert transacao.valor == Decimal("100.00")
        assert conta.saldo == Decimal("100.00")

    def test_item_de_venda_liquidada_nao_pode_ser_excluido(self, setup_data):
        empresa, cliente = setup_data
        venda = Venda.objects.create(empresa=empresa, cliente=cliente, status="confirmada")
        item = ItemVenda.objects.create(
            venda=venda,
            produto_nome="Produto não excluir",
            quantidade=1,
            preco_unitario=Decimal("80.00"),
        )
        transacao = venda.transacao_financeira
        transacao.paga = True
        transacao.save(update_fields=['paga', 'atualizado_em'])

        with pytest.raises(ValidationError):
            item.delete()

        assert ItemVenda.objects.filter(pk=item.pk).exists()
        venda.refresh_from_db()
        transacao.refresh_from_db()
        assert venda.valor_total == Decimal("80.00")
        assert transacao.valor == Decimal("80.00")

    def test_venda_liquidada_exige_estorno_antes_da_exclusao(self, setup_data):
        empresa, cliente = setup_data
        venda = Venda.objects.create(empresa=empresa, cliente=cliente, status="confirmada")
        ItemVenda.objects.create(
            venda=venda,
            produto_nome="Venda não excluir",
            quantidade=1,
            preco_unitario=Decimal("90.00"),
        )
        transacao = venda.transacao_financeira
        transacao.paga = True
        transacao.save(update_fields=['paga', 'atualizado_em'])

        with pytest.raises(ValidationError):
            venda.delete()

        assert Venda.objects.filter(pk=venda.pk).exists()
        assert ItemVenda.objects.filter(venda=venda).exists()
        assert type(transacao).objects.filter(pk=transacao.pk, paga=True).exists()

    def test_venda_liquidada_nao_aceita_novo_item(self, setup_data):
        empresa, cliente = setup_data
        venda = Venda.objects.create(empresa=empresa, cliente=cliente, status="confirmada")
        item_original = ItemVenda.objects.create(
            venda=venda,
            produto_nome="Item original",
            quantidade=1,
            preco_unitario=Decimal("50.00"),
        )
        transacao = venda.transacao_financeira
        transacao.paga = True
        transacao.save(update_fields=['paga', 'atualizado_em'])

        novo_item = ItemVenda(
            venda=venda,
            produto_nome="Item posterior à liquidação",
            quantidade=1,
            preco_unitario=Decimal("25.00"),
        )
        with pytest.raises(ValidationError):
            novo_item.save()

        assert list(ItemVenda.objects.filter(venda=venda)) == [item_original]
        venda.refresh_from_db()
        transacao.refresh_from_db()
        assert venda.valor_total == Decimal("50.00")
        assert transacao.valor == Decimal("50.00")

    def test_apos_estorno_venda_e_item_podem_ser_alterados(self, setup_data):
        empresa, cliente = setup_data
        venda = Venda.objects.create(empresa=empresa, cliente=cliente, status="confirmada")
        item = ItemVenda.objects.create(
            venda=venda,
            produto_nome="Item estornado",
            quantidade=1,
            preco_unitario=Decimal("100.00"),
        )
        transacao = venda.transacao_financeira
        transacao.paga = True
        transacao.save(update_fields=['paga', 'atualizado_em'])
        transacao.paga = False
        transacao.save(update_fields=['paga', 'atualizado_em'])

        item.preco_unitario = Decimal("120.00")
        item.save()
        venda.desconto = Decimal("20.00")
        venda.recalcular_totais()

        item.refresh_from_db()
        venda.refresh_from_db()
        transacao.refresh_from_db()
        assert item.preco_unitario == Decimal("120.00")
        assert venda.valor_total == Decimal("100.00")
        assert transacao.valor == Decimal("100.00")
        assert transacao.paga is False

    def test_queryset_update_nao_altera_venda_liquidada(self, setup_data):
        empresa, cliente = setup_data
        venda = Venda.objects.create(empresa=empresa, cliente=cliente, status="confirmada")
        ItemVenda.objects.create(
            venda=venda,
            produto_nome="Venda bulk",
            quantidade=1,
            preco_unitario=Decimal("75.00"),
        )
        transacao = venda.transacao_financeira
        transacao.paga = True
        transacao.save(update_fields=['paga', 'atualizado_em'])

        with pytest.raises(DatabaseError):
            with transaction.atomic():
                Venda.objects.filter(pk=venda.pk).update(desconto=Decimal("10.00"))

        venda.refresh_from_db()
        assert venda.desconto == Decimal("0.00")

    def test_queryset_update_nao_altera_item_de_venda_liquidada(self, setup_data):
        empresa, cliente = setup_data
        venda = Venda.objects.create(empresa=empresa, cliente=cliente, status="confirmada")
        item = ItemVenda.objects.create(
            venda=venda,
            produto_nome="Item bulk",
            quantidade=1,
            preco_unitario=Decimal("85.00"),
        )
        transacao = venda.transacao_financeira
        transacao.paga = True
        transacao.save(update_fields=['paga', 'atualizado_em'])

        with pytest.raises(DatabaseError):
            with transaction.atomic():
                ItemVenda.objects.filter(pk=item.pk).update(preco_unitario=Decimal("5.00"))

        item.refresh_from_db()
        assert item.preco_unitario == Decimal("85.00")

    def test_queryset_delete_nao_exclui_venda_liquidada(self, setup_data):
        empresa, cliente = setup_data
        venda = Venda.objects.create(empresa=empresa, cliente=cliente, status="confirmada")
        ItemVenda.objects.create(
            venda=venda,
            produto_nome="Venda queryset delete",
            quantidade=1,
            preco_unitario=Decimal("95.00"),
        )
        transacao = venda.transacao_financeira
        transacao.paga = True
        transacao.save(update_fields=['paga', 'atualizado_em'])

        with pytest.raises(DatabaseError):
            with transaction.atomic():
                Venda.objects.filter(pk=venda.pk).delete()

        assert Venda.objects.filter(pk=venda.pk).exists()
        assert type(transacao).objects.filter(pk=transacao.pk, paga=True).exists()

    def test_queryset_delete_nao_exclui_item_de_venda_liquidada(self, setup_data):
        empresa, cliente = setup_data
        venda = Venda.objects.create(empresa=empresa, cliente=cliente, status="confirmada")
        item = ItemVenda.objects.create(
            venda=venda,
            produto_nome="Item queryset delete",
            quantidade=1,
            preco_unitario=Decimal("65.00"),
        )
        transacao = venda.transacao_financeira
        transacao.paga = True
        transacao.save(update_fields=['paga', 'atualizado_em'])

        with pytest.raises(DatabaseError):
            with transaction.atomic():
                ItemVenda.objects.filter(pk=item.pk).delete()

        assert ItemVenda.objects.filter(pk=item.pk).exists()

    def test_bulk_create_nao_adiciona_item_em_venda_liquidada(self, setup_data):
        empresa, cliente = setup_data
        venda = Venda.objects.create(empresa=empresa, cliente=cliente, status="confirmada")
        ItemVenda.objects.create(
            venda=venda,
            produto_nome="Item inicial bulk",
            quantidade=1,
            preco_unitario=Decimal("55.00"),
        )
        transacao = venda.transacao_financeira
        transacao.paga = True
        transacao.save(update_fields=['paga', 'atualizado_em'])

        with pytest.raises(DatabaseError):
            with transaction.atomic():
                ItemVenda.objects.bulk_create([
                    ItemVenda(
                        venda=venda,
                        produto_nome="Item bulk indevido",
                        quantidade=1,
                        preco_unitario=Decimal("10.00"),
                        subtotal=Decimal("10.00"),
                    )
                ])

        assert not ItemVenda.objects.filter(produto_nome="Item bulk indevido").exists()

    def test_exclusao_http_de_venda_liquidada_e_controlada(self, client, db):
        from datetime import date
        from meigestao_app.financeiro.models import ContaBancaria

        empresa = Empresa.objects.create(nome='Empresa exclusão HTTP', cnpj='85.963.741/0001-20')
        cliente = Cliente.objects.create(
            empresa=empresa,
            nome='Cliente exclusão HTTP',
            cpf_cnpj='852.963.741-00',
        )
        user = User.objects.create_user(username='excluir_venda_paga', password='senha')
        Perfil.objects.create(
            usuario=user,
            empresa=empresa,
            permissao='admin',
            data_admissao=date.today(),
        )
        conta = ContaBancaria.objects.create(
            empresa=empresa,
            banco='Banco exclusão HTTP',
            agencia='0003',
            conta='34567-8',
            saldo=Decimal('0.00'),
        )
        venda = Venda.objects.create(empresa=empresa, cliente=cliente, status='confirmada')
        ItemVenda.objects.create(
            venda=venda,
            produto_nome='Produto exclusão HTTP',
            quantidade=1,
            preco_unitario=Decimal('200.00'),
        )
        transacao = venda.transacao_financeira
        transacao.conta = conta
        transacao.paga = True
        transacao.save(update_fields=['conta', 'paga', 'atualizado_em'])
        client.force_login(user)

        response = client.post(reverse('vendas:venda_delete', kwargs={'pk': venda.pk}))

        assert response.status_code == 302
        assert Venda.objects.filter(pk=venda.pk).exists()
        assert ItemVenda.objects.filter(venda=venda).exists()
        assert type(transacao).objects.filter(pk=transacao.pk, paga=True).exists()
        conta.refresh_from_db()
        assert conta.saldo == Decimal('200.00')

    def test_save_da_venda_reverte_persistencia_se_sincronizacao_falhar(
        self, setup_data, monkeypatch
    ):
        empresa, cliente = setup_data
        venda = Venda.objects.create(empresa=empresa, cliente=cliente, status='rascunho')

        def falhar_sincronizacao():
            raise RuntimeError('falha simulada na sincronização')

        monkeypatch.setattr(venda, 'sincronizar_transacao_financeira', falhar_sincronizacao)
        venda.desconto = Decimal('15.00')

        with pytest.raises(RuntimeError):
            venda.save()

        venda.refresh_from_db()
        assert venda.desconto == Decimal('0.00')

    def test_save_do_item_reverte_persistencia_se_recalculo_falhar(
        self, setup_data, monkeypatch
    ):
        empresa, cliente = setup_data
        venda = Venda.objects.create(empresa=empresa, cliente=cliente, status='rascunho')
        item = ItemVenda.objects.create(
            venda=venda,
            produto_nome='Item atômico',
            quantidade=1,
            preco_unitario=Decimal('40.00'),
        )

        def falhar_recalculo(*args, **kwargs):
            raise RuntimeError('falha simulada no recálculo')

        monkeypatch.setattr(venda, 'recalcular_totais', falhar_recalculo)
        item.preco_unitario = Decimal('70.00')

        with pytest.raises(RuntimeError):
            item.save()

        item.refresh_from_db()
        assert item.preco_unitario == Decimal('40.00')
        assert item.subtotal == Decimal('40.00')

    def test_update_fields_do_item_tambem_persiste_subtotal(self, setup_data):
        empresa, cliente = setup_data
        venda = Venda.objects.create(empresa=empresa, cliente=cliente, status='confirmada')
        item = ItemVenda.objects.create(
            venda=venda,
            produto_nome='Item update_fields',
            quantidade=2,
            preco_unitario=Decimal('25.00'),
        )

        item.preco_unitario = Decimal('40.00')
        item.save(update_fields=['preco_unitario'])

        item.refresh_from_db()
        venda.refresh_from_db()
        transacao = venda.transacao_financeira
        assert item.subtotal == Decimal('80.00')
        assert venda.valor_total == Decimal('80.00')
        assert transacao.valor == Decimal('80.00')

    def test_exclusao_em_cascata_nao_remove_venda_liquidada(self, setup_data):
        empresa, cliente = setup_data
        venda = Venda.objects.create(empresa=empresa, cliente=cliente, status='confirmada')
        ItemVenda.objects.create(
            venda=venda,
            produto_nome='Venda protegida de cascata',
            quantidade=1,
            preco_unitario=Decimal('160.00'),
        )
        transacao = venda.transacao_financeira
        transacao.paga = True
        transacao.save(update_fields=['paga', 'atualizado_em'])

        with pytest.raises(DatabaseError):
            with transaction.atomic():
                cliente.delete()

        assert Cliente.objects.filter(pk=cliente.pk).exists()
        assert Venda.objects.filter(pk=venda.pk).exists()
        assert type(transacao).objects.filter(pk=transacao.pk, venda=venda, paga=True).exists()

    def test_venda_estornada_pode_ser_excluida_por_queryset(self, setup_data):
        empresa, cliente = setup_data
        venda = Venda.objects.create(empresa=empresa, cliente=cliente, status='confirmada')
        ItemVenda.objects.create(
            venda=venda,
            produto_nome='Venda estornada queryset',
            quantidade=1,
            preco_unitario=Decimal('180.00'),
        )
        transacao = venda.transacao_financeira
        transacao.paga = False
        transacao.save(update_fields=['paga', 'atualizado_em'])

        Venda.objects.filter(pk=venda.pk).delete()

        assert not Venda.objects.filter(pk=venda.pk).exists()
        assert not type(transacao).objects.filter(pk=transacao.pk).exists()

    def test_venda_estornada_pode_ser_excluida_em_cascata(self, setup_data):
        empresa, cliente = setup_data
        venda = Venda.objects.create(empresa=empresa, cliente=cliente, status='confirmada')
        ItemVenda.objects.create(
            venda=venda,
            produto_nome='Venda estornada cascata',
            quantidade=1,
            preco_unitario=Decimal('185.00'),
        )
        transacao = venda.transacao_financeira
        transacao.paga = False
        transacao.save(update_fields=['paga', 'atualizado_em'])

        cliente.delete()

        assert not Cliente.objects.filter(pk=cliente.pk).exists()
        assert not Venda.objects.filter(pk=venda.pk).exists()
        assert not type(transacao).objects.filter(pk=transacao.pk).exists()

    def test_nota_fiscal_generation(self, setup_data):
        empresa, cliente = setup_data
        venda = Venda.objects.create(empresa=empresa, cliente=cliente, valor_total=100.00)
        
        nf = venda.gerar_nota_fiscal()
        
        assert nf.venda == venda
        assert nf.cliente == cliente
        assert nf.status == 'rascunho'
        assert nf.numero.startswith(str(timezone.now().year))
