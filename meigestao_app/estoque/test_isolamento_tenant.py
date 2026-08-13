from datetime import date

import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from meigestao_app.core.models import Empresa
from meigestao_app.estoque.models import Categoria, Estoque, Produto
from meigestao_app.usuarios.models import Perfil


@pytest.fixture
def empresas_com_usuario_e_estoque(db):
    empresa_a = Empresa.objects.create(
        nome="Empresa A",
        cnpj="11.111.111/0001-11",
    )
    empresa_b = Empresa.objects.create(
        nome="Empresa B",
        cnpj="22.222.222/0001-22",
    )
    usuario_a = User.objects.create_user(
        username="usuario_a",
        password="senha-forte-de-teste",
    )
    Perfil.objects.create(
        usuario=usuario_a,
        empresa=empresa_a,
        data_admissao=date.today(),
    )
    categoria_b = Categoria.objects.create(
        empresa=empresa_b,
        nome="Categoria B",
    )
    produto_b = Produto.objects.create(
        empresa=empresa_b,
        categoria=categoria_b,
        nome="Produto exclusivo da B",
        sku="B-001",
        preco_custo="10.00",
        preco_venda="20.00",
    )
    estoque_b = Estoque.objects.create(
        empresa=empresa_b,
        produto=produto_b,
        quantidade=15,
    )
    return usuario_a, categoria_b, produto_b, estoque_b


@pytest.mark.django_db
class TestIsolamentoEstoqueEntreEmpresas:
    def test_formulario_produto_nao_lista_categoria_de_outra_empresa(
        self, client, empresas_com_usuario_e_estoque
    ):
        usuario_a, categoria_b, _, _ = empresas_com_usuario_e_estoque
        categoria_a = Categoria.objects.create(
            empresa=usuario_a.perfil.empresa,
            nome="Categoria A",
        )
        client.force_login(usuario_a)

        response = client.get(reverse("estoque:produto_create"))

        assert response.status_code == 200
        queryset = response.context["form"].fields["categoria"].queryset
        assert categoria_a in queryset
        assert categoria_b not in queryset

    def test_post_nao_cria_produto_com_categoria_de_outra_empresa(
        self, client, empresas_com_usuario_e_estoque
    ):
        usuario_a, categoria_b, _, _ = empresas_com_usuario_e_estoque
        client.force_login(usuario_a)

        response = client.post(
            reverse("estoque:produto_create"),
            {
                "categoria": categoria_b.pk,
                "nome": "Produto cruzado",
                "sku": "CRUZADO-001",
                "descricao": "Tentativa cross-tenant",
                "preco_custo": "10.00",
                "preco_venda": "20.00",
                "ativo": "on",
            },
        )

        assert response.status_code == 200
        assert not Produto.objects.filter(sku="CRUZADO-001").exists()
        assert "categoria" in response.context["form"].errors

    def test_usuario_nao_visualiza_categoria_de_outra_empresa(
        self, client, empresas_com_usuario_e_estoque
    ):
        usuario_a, categoria_b, _, _ = empresas_com_usuario_e_estoque
        client.force_login(usuario_a)

        response = client.get(
            reverse("estoque:categoria_detail", kwargs={"pk": categoria_b.pk})
        )

        assert response.status_code == 404

    def test_usuario_nao_visualiza_produto_de_outra_empresa(
        self, client, empresas_com_usuario_e_estoque
    ):
        usuario_a, _, produto_b, _ = empresas_com_usuario_e_estoque
        client.force_login(usuario_a)

        response = client.get(
            reverse("estoque:produto_detail", kwargs={"pk": produto_b.pk})
        )

        assert response.status_code == 404

    def test_usuario_nao_abre_edicao_de_produto_de_outra_empresa(
        self, client, empresas_com_usuario_e_estoque
    ):
        usuario_a, _, produto_b, _ = empresas_com_usuario_e_estoque
        client.force_login(usuario_a)

        response = client.get(
            reverse("estoque:produto_update", kwargs={"pk": produto_b.pk})
        )

        assert response.status_code == 404

    def test_usuario_nao_exclui_produto_de_outra_empresa(
        self, client, empresas_com_usuario_e_estoque
    ):
        usuario_a, _, produto_b, _ = empresas_com_usuario_e_estoque
        client.force_login(usuario_a)

        response = client.post(
            reverse("estoque:produto_delete", kwargs={"pk": produto_b.pk})
        )

        assert response.status_code == 404
        assert Produto.objects.filter(pk=produto_b.pk).exists()

    def test_usuario_nao_visualiza_estoque_de_produto_de_outra_empresa(
        self, client, empresas_com_usuario_e_estoque
    ):
        usuario_a, _, produto_b, _ = empresas_com_usuario_e_estoque
        client.force_login(usuario_a)

        response = client.get(
            reverse("estoque:estoque_detail", kwargs={"pk": produto_b.pk})
        )

        assert response.status_code == 404

    def test_usuario_nao_movimenta_produto_de_outra_empresa(
        self, client, empresas_com_usuario_e_estoque
    ):
        usuario_a, _, produto_b, estoque_b = empresas_com_usuario_e_estoque
        client.force_login(usuario_a)

        response = client.post(
            reverse(
                "estoque:movimentacao_create",
                kwargs={"produto_id": produto_b.pk},
            ),
            {
                "tipo_movimento": "saida",
                "quantidade": 5,
                "motivo": "Tentativa cruzada",
            },
        )

        assert response.status_code == 404
        estoque_b.refresh_from_db()
        assert estoque_b.quantidade == 15
