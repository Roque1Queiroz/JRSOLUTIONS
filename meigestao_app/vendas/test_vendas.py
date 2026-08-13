from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
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

        with pytest.raises(IntegrityError):
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

        with pytest.raises(IntegrityError):
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

        with pytest.raises(IntegrityError):
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

        with pytest.raises(IntegrityError):
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

        with pytest.raises(IntegrityError):
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

        with pytest.raises(IntegrityError):
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
