from datetime import date

import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from meigestao_app.core.models import Empresa
from meigestao_app.estoque.models import Categoria, Produto
from meigestao_app.producao.models import FichaTecnica, OrdemProducao
from meigestao_app.usuarios.models import Perfil


@pytest.fixture
def empresas_com_usuario_e_producao(db):
    empresa_a = Empresa.objects.create(
        nome="Produção A",
        cnpj="61.111.111/0001-61",
        plano="profissional",
    )
    empresa_b = Empresa.objects.create(
        nome="Produção B",
        cnpj="62.222.222/0001-62",
        plano="profissional",
    )
    usuario_a = User.objects.create_user(
        username="producao_a",
        password="senha-forte-de-teste",
    )
    Perfil.objects.create(
        usuario=usuario_a,
        empresa=empresa_a,
        data_admissao=date.today(),
        permissao="admin",
    )
    categoria_a = Categoria.objects.create(empresa=empresa_a, nome="Categoria A")
    categoria_b = Categoria.objects.create(empresa=empresa_b, nome="Categoria B")
    produto_a = Produto.objects.create(
        empresa=empresa_a,
        categoria=categoria_a,
        nome="Produto A",
        sku="PROD-A-001",
        preco_custo="10.00",
        preco_venda="20.00",
    )
    produto_b = Produto.objects.create(
        empresa=empresa_b,
        categoria=categoria_b,
        nome="Produto B",
        sku="PROD-B-001",
        preco_custo="10.00",
        preco_venda="20.00",
    )
    ficha_a = FichaTecnica.objects.create(
        empresa=empresa_a,
        produto_final=produto_a,
    )
    ficha_b = FichaTecnica.objects.create(
        empresa=empresa_b,
        produto_final=produto_b,
    )
    ordem_b = OrdemProducao.objects.create(
        empresa=empresa_b,
        ficha_tecnica=ficha_b,
    )
    return usuario_a, produto_a, produto_b, ficha_a, ficha_b, ordem_b


@pytest.mark.django_db
class TestIsolamentoProducaoEntreEmpresas:
    def test_usuario_nao_visualiza_ordem_de_outra_empresa(
        self, client, empresas_com_usuario_e_producao
    ):
        usuario_a, *_, ordem_b = empresas_com_usuario_e_producao
        client.force_login(usuario_a)

        response = client.get(
            reverse("producao:ordem_producao_detail", kwargs={"pk": ordem_b.pk})
        )

        assert response.status_code == 404

    def test_formulario_ficha_lista_apenas_produtos_da_empresa(
        self, client, empresas_com_usuario_e_producao
    ):
        usuario_a, produto_a, produto_b, *_ = empresas_com_usuario_e_producao
        client.force_login(usuario_a)

        response = client.get(reverse("producao:ficha_tecnica_create"))

        assert response.status_code == 200
        queryset = response.context["form"].fields["produto_final"].queryset
        assert produto_a in queryset
        assert produto_b not in queryset

    def test_formulario_ordem_lista_apenas_fichas_da_empresa(
        self, client, empresas_com_usuario_e_producao
    ):
        usuario_a, _, _, ficha_a, ficha_b, _ = empresas_com_usuario_e_producao
        client.force_login(usuario_a)

        response = client.get(reverse("producao:ordem_producao_create"))

        assert response.status_code == 200
        queryset = response.context["form"].fields["ficha_tecnica"].queryset
        assert ficha_a in queryset
        assert ficha_b not in queryset
