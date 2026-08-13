import pytest
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
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

    def test_nota_fiscal_generation(self, setup_data):
        empresa, cliente = setup_data
        venda = Venda.objects.create(empresa=empresa, cliente=cliente, valor_total=100.00)
        
        nf = venda.gerar_nota_fiscal()
        
        assert nf.venda == venda
        assert nf.cliente == cliente
        assert nf.status == 'rascunho'
        assert nf.numero.startswith(str(timezone.now().year))
