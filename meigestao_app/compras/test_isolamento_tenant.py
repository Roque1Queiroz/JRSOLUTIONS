from datetime import date

import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from meigestao_app.compras.models import (
    Cotacao,
    Fornecedor,
    ItemPedidoCompra,
    PedidoCompra,
)
from meigestao_app.core.models import Empresa
from meigestao_app.estoque.models import Categoria, Produto
from meigestao_app.financeiro.models import Transacao
from meigestao_app.usuarios.models import Perfil


@pytest.fixture
def empresas_com_usuario_e_pedido(db):
    empresa_a = Empresa.objects.create(
        nome="Compras A", cnpj="41.111.111/0001-41", plano="profissional"
    )
    empresa_b = Empresa.objects.create(
        nome="Compras B", cnpj="42.222.222/0001-42", plano="profissional"
    )
    usuario_a = User.objects.create_user(
        username="compras_a", password="senha-forte-de-teste"
    )
    Perfil.objects.create(
        usuario=usuario_a,
        empresa=empresa_a,
        data_admissao=date.today(),
        permissao="admin",
    )
    pedido_a = PedidoCompra.objects.create(
        empresa=empresa_a, observacoes="Pedido legítimo da A"
    )
    pedido_b = PedidoCompra.objects.create(
        empresa=empresa_b, observacoes="Pedido exclusivo da B"
    )
    categoria_b = Categoria.objects.create(empresa=empresa_b, nome="Categoria B")
    produto_b = Produto.objects.create(
        empresa=empresa_b,
        categoria=categoria_b,
        nome="Produto B",
        sku="COMP-B-001",
        preco_custo="10.00",
        preco_venda="20.00",
    )
    fornecedor_b = Fornecedor.objects.create(empresa=empresa_b, nome="Fornecedor B")
    return usuario_a, pedido_a, pedido_b, produto_b, fornecedor_b


@pytest.mark.django_db
class TestIsolamentoComprasEntreEmpresas:
    def test_receber_mesmo_pedido_duas_vezes_nao_duplica_despesa(
        self, client, empresas_com_usuario_e_pedido
    ):
        usuario_a, pedido_a, _, _, _ = empresas_com_usuario_e_pedido
        client.force_login(usuario_a)
        url = reverse("compras:pedido_detail", kwargs={"pk": pedido_a.pk})

        primeira_resposta = client.post(url, {"receber_mercadoria": "1"})
        segunda_resposta = client.post(url, {"receber_mercadoria": "1"})

        assert primeira_resposta.status_code == 302
        assert segunda_resposta.status_code == 302
        pedido_a.refresh_from_db()
        assert pedido_a.status == "RECEBIDO"
        assert Transacao.objects.filter(
            empresa=pedido_a.empresa,
            descricao__startswith=f"Compra #{pedido_a.id}",
        ).count() == 1

    def test_usuario_nao_visualiza_pedido_de_outra_empresa(
        self, client, empresas_com_usuario_e_pedido
    ):
        usuario_a, _, pedido_b, _, _ = empresas_com_usuario_e_pedido
        client.force_login(usuario_a)
        response = client.get(
            reverse("compras:pedido_detail", kwargs={"pk": pedido_b.pk})
        )
        assert response.status_code == 404

    def test_usuario_nao_executa_acao_em_pedido_de_outra_empresa(
        self, client, empresas_com_usuario_e_pedido
    ):
        usuario_a, _, pedido_b, _, _ = empresas_com_usuario_e_pedido
        client.force_login(usuario_a)
        response = client.post(
            reverse("compras:pedido_detail", kwargs={"pk": pedido_b.pk}),
            {"receber_mercadoria": "1"},
        )
        assert response.status_code == 404
        pedido_b.refresh_from_db()
        assert pedido_b.status == "SOLICITADO"

    def test_usuario_nao_adiciona_produto_de_outra_empresa_em_pedido_proprio(
        self, client, empresas_com_usuario_e_pedido
    ):
        usuario_a, pedido_a, _, produto_b, _ = empresas_com_usuario_e_pedido
        client.force_login(usuario_a)
        response = client.post(
            reverse("compras:pedido_detail", kwargs={"pk": pedido_a.pk}),
            {"add_item": "1", "produto_id": produto_b.pk, "quantidade": 2},
        )
        assert response.status_code == 404
        assert not ItemPedidoCompra.objects.filter(
            pedido_compra=pedido_a, produto=produto_b
        ).exists()

    def test_usuario_nao_adiciona_fornecedor_de_outra_empresa_em_pedido_proprio(
        self, client, empresas_com_usuario_e_pedido
    ):
        usuario_a, pedido_a, _, _, fornecedor_b = empresas_com_usuario_e_pedido
        client.force_login(usuario_a)
        response = client.post(
            reverse("compras:pedido_detail", kwargs={"pk": pedido_a.pk}),
            {
                "add_cotacao": "1",
                "fornecedor_id": fornecedor_b.pk,
                "valor_total": "100.00",
                "prazo": 10,
                "condicoes": "À vista",
            },
        )
        assert response.status_code == 404
        assert not Cotacao.objects.filter(
            pedido_compra=pedido_a, fornecedor=fornecedor_b
        ).exists()
