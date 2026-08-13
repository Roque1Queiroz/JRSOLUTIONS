from datetime import date

import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from meigestao_app.core.models import Empresa
from meigestao_app.estoque.models import (
    Categoria,
    Estoque,
    MovimentacaoEstoque,
    Produto,
)
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

    def test_vendedor_nao_registra_movimentacao_manual(self, client, db):
        empresa = Empresa.objects.create(nome="Estoque RBAC", cnpj="31.313.131/0001-31")
        user = User.objects.create_user(username="vendedor_estoque", password="password")
        Perfil.objects.create(
            usuario=user,
            empresa=empresa,
            data_admissao=date.today(),
            permissao="vendedor",
        )
        categoria = Categoria.objects.create(empresa=empresa, nome="Categoria RBAC")
        produto = Produto.objects.create(
            empresa=empresa,
            categoria=categoria,
            nome="Produto RBAC",
            sku="EST-RBAC-001",
            preco_custo="10.00",
            preco_venda="20.00",
        )
        estoque = Estoque.objects.create(empresa=empresa, produto=produto, quantidade=10)
        client.login(username="vendedor_estoque", password="password")

        response = client.post(
            reverse("estoque:movimentacao_create", kwargs={"produto_id": produto.pk}),
            {
                "tipo_movimento": "entrada",
                "quantidade": 5,
                "motivo": "Entrada indevida",
            },
        )

        assert response.status_code == 403
        estoque.refresh_from_db()
        assert estoque.quantidade == 10
        assert not MovimentacaoEstoque.objects.filter(
            produto=produto,
            motivo="Entrada indevida",
        ).exists()

    @pytest.mark.parametrize(
        ('username', 'permissao', 'ativo', 'is_staff', 'esperado'),
        [
            ('admin_estoque', 'admin', True, False, 302),
            ('gerente_estoque', 'gerente', True, False, 302),
            ('almoxarife_estoque', 'almoxarife', True, False, 302),
            ('perfil_inativo_estoque', 'almoxarife', False, False, 403),
            ('staff_vendedor_estoque', 'vendedor', True, True, 403),
            ('operador_estoque', 'operador', True, False, 403),
        ],
    )
    def test_matriz_movimentacao_manual(
        self, client, db, username, permissao, ativo, is_staff, esperado
    ):
        cnpjs = {
            'admin_estoque': '30.303.030/0001-30',
            'gerente_estoque': '36.767.676/0001-36',
            'almoxarife_estoque': '32.323.232/0001-32',
            'perfil_inativo_estoque': '33.434.343/0001-33',
            'staff_vendedor_estoque': '34.545.454/0001-34',
            'operador_estoque': '41.212.121/0001-41',
        }
        empresa = Empresa.objects.create(nome=f"Empresa {username}", cnpj=cnpjs[username])
        user = User.objects.create_user(
            username=username,
            password="password",
            is_staff=is_staff,
        )
        Perfil.objects.create(
            usuario=user,
            empresa=empresa,
            data_admissao=date.today(),
            permissao=permissao,
            ativo=ativo,
        )
        categoria = Categoria.objects.create(empresa=empresa, nome=f"Categoria {username}")
        produto = Produto.objects.create(
            empresa=empresa,
            categoria=categoria,
            nome=f"Produto {username}",
            sku=f"SKU-{username}",
            preco_custo="10.00",
            preco_venda="20.00",
        )
        estoque = Estoque.objects.create(empresa=empresa, produto=produto, quantidade=10)
        client.login(username=username, password="password")

        response = client.post(
            reverse("estoque:movimentacao_create", kwargs={"produto_id": produto.pk}),
            {
                "tipo_movimento": "entrada",
                "quantidade": 5,
                "motivo": f"Movimento {username}",
            },
        )

        assert response.status_code == esperado
        estoque.refresh_from_db()
        quantidade_esperada = 15 if esperado == 302 else 10
        assert estoque.quantidade == quantidade_esperada
        assert MovimentacaoEstoque.objects.filter(
            produto=produto,
            motivo=f"Movimento {username}",
        ).exists() is (esperado == 302)

    @pytest.mark.parametrize('permissao', ['admin', 'gerente', 'almoxarife'])
    @pytest.mark.parametrize(
        ('tipo_movimento', 'quantidade', 'saldo_esperado'),
        [('saida', 3, 7), ('devolucao', 4, 14)],
    )
    def test_papeis_autorizados_fazem_saida_e_devolucao(
        self, client, db, permissao, tipo_movimento, quantidade, saldo_esperado
    ):
        sufixos = {
            ('admin', 'saida'): ('42.323.232/0001-42', 'AS'),
            ('admin', 'devolucao'): ('43.434.343/0001-43', 'AD'),
            ('gerente', 'saida'): ('44.545.454/0001-44', 'GS'),
            ('gerente', 'devolucao'): ('45.656.565/0001-45', 'GD'),
            ('almoxarife', 'saida'): ('46.767.676/0001-46', 'XS'),
            ('almoxarife', 'devolucao'): ('47.878.787/0001-47', 'XD'),
        }
        cnpj, sufixo = sufixos[(permissao, tipo_movimento)]
        username = f"{permissao}_{tipo_movimento}_estoque"
        empresa = Empresa.objects.create(nome=f"Empresa {username}", cnpj=cnpj)
        user = User.objects.create_user(username=username, password="password")
        Perfil.objects.create(
            usuario=user,
            empresa=empresa,
            data_admissao=date.today(),
            permissao=permissao,
        )
        categoria = Categoria.objects.create(empresa=empresa, nome=f"Categoria {sufixo}")
        produto = Produto.objects.create(
            empresa=empresa,
            categoria=categoria,
            nome=f"Produto {sufixo}",
            sku=f"SKU-MOV-{sufixo}",
            preco_custo="10.00",
            preco_venda="20.00",
        )
        estoque = Estoque.objects.create(empresa=empresa, produto=produto, quantidade=10)
        motivo = f"{tipo_movimento} legítima {permissao}"
        client.login(username=username, password="password")

        response = client.post(
            reverse("estoque:movimentacao_create", kwargs={"produto_id": produto.pk}),
            {
                "tipo_movimento": tipo_movimento,
                "quantidade": quantidade,
                "motivo": motivo,
            },
        )

        assert response.status_code == 302
        estoque.refresh_from_db()
        assert estoque.quantidade == saldo_esperado
        assert MovimentacaoEstoque.objects.filter(
            produto=produto,
            tipo_movimento=tipo_movimento,
            motivo=motivo,
        ).exists()

    def test_almoxarife_nao_faz_ajuste_absoluto_de_saldo(self, client, db):
        empresa = Empresa.objects.create(nome="Empresa Ajuste Restrito", cnpj="38.989.898/0001-38")
        user = User.objects.create_user(username="almox_ajuste", password="password")
        Perfil.objects.create(
            usuario=user,
            empresa=empresa,
            data_admissao=date.today(),
            permissao="almoxarife",
        )
        categoria = Categoria.objects.create(empresa=empresa, nome="Categoria Ajuste")
        produto = Produto.objects.create(
            empresa=empresa,
            categoria=categoria,
            nome="Produto Ajuste",
            sku="SKU-AJUSTE-RESTRITO",
            preco_custo="10.00",
            preco_venda="20.00",
        )
        estoque = Estoque.objects.create(empresa=empresa, produto=produto, quantidade=10)
        client.login(username="almox_ajuste", password="password")

        response = client.post(
            reverse("estoque:movimentacao_create", kwargs={"produto_id": produto.pk}),
            {
                "tipo_movimento": "ajuste",
                "quantidade": 999,
                "motivo": "Ajuste absoluto indevido",
            },
        )

        assert response.status_code == 403
        estoque.refresh_from_db()
        assert estoque.quantidade == 10
        assert not MovimentacaoEstoque.objects.filter(
            produto=produto,
            motivo="Ajuste absoluto indevido",
        ).exists()

    @pytest.mark.parametrize('permissao', ['admin', 'gerente'])
    def test_admin_e_gerente_fazem_ajuste_absoluto(self, client, db, permissao):
        empresa = Empresa.objects.create(
            nome=f"Empresa Ajuste {permissao}",
            cnpj={'admin': '39.090.909/0001-39', 'gerente': '40.101.010/0001-40'}[permissao],
        )
        user = User.objects.create_user(username=f"{permissao}_ajuste", password="password")
        Perfil.objects.create(
            usuario=user,
            empresa=empresa,
            data_admissao=date.today(),
            permissao=permissao,
        )
        categoria = Categoria.objects.create(empresa=empresa, nome=f"Categoria {permissao}")
        produto = Produto.objects.create(
            empresa=empresa,
            categoria=categoria,
            nome=f"Produto {permissao}",
            sku=f"SKU-AJUSTE-{permissao.upper()}",
            preco_custo="10.00",
            preco_venda="20.00",
        )
        estoque = Estoque.objects.create(empresa=empresa, produto=produto, quantidade=10)
        client.login(username=f"{permissao}_ajuste", password="password")

        response = client.post(
            reverse("estoque:movimentacao_create", kwargs={"produto_id": produto.pk}),
            {
                "tipo_movimento": "ajuste",
                "quantidade": 25,
                "motivo": f"Ajuste legítimo {permissao}",
            },
        )

        assert response.status_code == 302
        estoque.refresh_from_db()
        assert estoque.quantidade == 25
        assert MovimentacaoEstoque.objects.filter(
            produto=produto,
            tipo_movimento='ajuste',
            motivo=f"Ajuste legítimo {permissao}",
        ).exists()

    def test_usuario_sem_perfil_nao_movimenta_estoque(self, client, db):
        empresa = Empresa.objects.create(nome="Empresa Sem Perfil Estoque", cnpj="37.878.787/0001-37")
        user = User.objects.create_user(username="sem_perfil_estoque", password="password")
        categoria = Categoria.objects.create(empresa=empresa, nome="Categoria Sem Perfil")
        produto = Produto.objects.create(
            empresa=empresa,
            categoria=categoria,
            nome="Produto Sem Perfil",
            sku="SKU-SEM-PERFIL-ESTOQUE",
            preco_custo="10.00",
            preco_venda="20.00",
        )
        estoque = Estoque.objects.create(empresa=empresa, produto=produto, quantidade=10)
        client.login(username="sem_perfil_estoque", password="password")

        response = client.post(
            reverse("estoque:movimentacao_create", kwargs={"produto_id": produto.pk}),
            {
                "tipo_movimento": "entrada",
                "quantidade": 5,
                "motivo": "Movimento sem perfil",
            },
        )

        assert response.status_code == 403
        estoque.refresh_from_db()
        assert estoque.quantidade == 10
        assert not MovimentacaoEstoque.objects.filter(
            produto=produto,
            motivo="Movimento sem perfil",
        ).exists()

    def test_usuario_anonimo_e_redirecionado_antes_do_rbac(self, client, db):
        response = client.get(
            reverse("estoque:movimentacao_create", kwargs={"produto_id": 999999})
        )

        assert response.status_code == 302
        assert 'login' in response.url

    def test_superusuario_faz_ajuste_absoluto(self, client, db):
        empresa = Empresa.objects.create(nome="Empresa Super Ajuste", cnpj="48.989.898/0001-48")
        user = User.objects.create_superuser(
            username="super_ajuste_estoque",
            password="password",
            email="superajuste@example.com",
        )
        Perfil.objects.create(
            usuario=user,
            empresa=empresa,
            data_admissao=date.today(),
            permissao="vendedor",
            ativo=False,
        )
        categoria = Categoria.objects.create(empresa=empresa, nome="Categoria Super Ajuste")
        produto = Produto.objects.create(
            empresa=empresa,
            categoria=categoria,
            nome="Produto Super Ajuste",
            sku="SKU-SUPER-AJUSTE",
            preco_custo="10.00",
            preco_venda="20.00",
        )
        estoque = Estoque.objects.create(empresa=empresa, produto=produto, quantidade=10)
        client.login(username="super_ajuste_estoque", password="password")

        response = client.post(
            reverse("estoque:movimentacao_create", kwargs={"produto_id": produto.pk}),
            {
                "tipo_movimento": "ajuste",
                "quantidade": 30,
                "motivo": "Ajuste superuser",
            },
        )

        assert response.status_code == 302
        estoque.refresh_from_db()
        assert estoque.quantidade == 30
        assert MovimentacaoEstoque.objects.filter(
            produto=produto,
            tipo_movimento='ajuste',
            motivo="Ajuste superuser",
        ).exists()

    def test_superusuario_movimenta_estoque_com_empresa(self, client, db):
        empresa = Empresa.objects.create(nome="Empresa Super Estoque", cnpj="35.656.565/0001-35")
        user = User.objects.create_superuser(
            username="super_estoque",
            password="password",
            email="superestoque@example.com",
        )
        Perfil.objects.create(
            usuario=user,
            empresa=empresa,
            data_admissao=date.today(),
            permissao="vendedor",
            ativo=False,
        )
        categoria = Categoria.objects.create(empresa=empresa, nome="Categoria Super")
        produto = Produto.objects.create(
            empresa=empresa,
            categoria=categoria,
            nome="Produto Super",
            sku="SKU-SUPER-ESTOQUE",
            preco_custo="10.00",
            preco_venda="20.00",
        )
        estoque = Estoque.objects.create(empresa=empresa, produto=produto, quantidade=10)
        client.login(username="super_estoque", password="password")

        response = client.post(
            reverse("estoque:movimentacao_create", kwargs={"produto_id": produto.pk}),
            {
                "tipo_movimento": "entrada",
                "quantidade": 5,
                "motivo": "Movimento superuser",
            },
        )

        assert response.status_code == 302
        estoque.refresh_from_db()
        assert estoque.quantidade == 15

    def test_usuario_nao_movimenta_produto_de_outra_empresa(
        self, client, empresas_com_usuario_e_estoque
    ):
        usuario_a, _, produto_b, estoque_b = empresas_com_usuario_e_estoque
        usuario_a.perfil.permissao = 'admin'
        usuario_a.perfil.save(update_fields=['permissao', 'atualizado_em'])
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
