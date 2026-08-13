import pytest
from django.utils import timezone
from django.urls import reverse
from meigestao_app.vendas.models import Venda, ItemVenda
from meigestao_app.clientes.models import Cliente
from meigestao_app.core.models import Empresa

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

    def test_nota_fiscal_generation(self, setup_data):
        empresa, cliente = setup_data
        venda = Venda.objects.create(empresa=empresa, cliente=cliente, valor_total=100.00)
        
        nf = venda.gerar_nota_fiscal()
        
        assert nf.venda == venda
        assert nf.cliente == cliente
        assert nf.status == 'rascunho'
        assert nf.numero.startswith(str(timezone.now().year))
