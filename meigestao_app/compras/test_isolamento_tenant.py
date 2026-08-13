from datetime import date

import pytest
from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
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

    def test_vendedor_nao_aprova_cotacao(self, client, db):
        empresa = Empresa.objects.create(
            nome="Compras RBAC A", cnpj="50.505.050/0001-50", plano="profissional"
        )
        user = User.objects.create_user(username="vendedor_compras", password="password")
        Perfil.objects.create(
            usuario=user,
            empresa=empresa,
            data_admissao=date.today(),
            permissao="vendedor",
        )
        pedido = PedidoCompra.objects.create(empresa=empresa)
        fornecedor = Fornecedor.objects.create(empresa=empresa, nome="Fornecedor RBAC")
        cotacao = Cotacao.objects.create(
            pedido_compra=pedido,
            fornecedor=fornecedor,
            valor_total="100.00",
            prazo_entrega_dias=5,
        )
        client.login(username="vendedor_compras", password="password")

        response = client.post(
            reverse("compras:pedido_detail", kwargs={"pk": pedido.pk}),
            {"aprovar_cotacao": cotacao.pk},
        )

        assert response.status_code == 403
        pedido.refresh_from_db()
        cotacao.refresh_from_db()
        assert pedido.status == "SOLICITADO"
        assert cotacao.vencedor is False

    def test_operador_nao_recebe_mercadoria(self, client, db):
        empresa = Empresa.objects.create(
            nome="Compras RBAC B", cnpj="60.606.060/0001-60", plano="profissional"
        )
        user = User.objects.create_user(username="operador_compras", password="password")
        Perfil.objects.create(
            usuario=user,
            empresa=empresa,
            data_admissao=date.today(),
            permissao="operador",
        )
        pedido = PedidoCompra.objects.create(empresa=empresa, status="APROVADO")
        client.login(username="operador_compras", password="password")

        response = client.post(
            reverse("compras:pedido_detail", kwargs={"pk": pedido.pk}),
            {"receber_mercadoria": "1"},
        )

        assert response.status_code == 403
        pedido.refresh_from_db()
        assert pedido.status == "APROVADO"
        assert not Transacao.objects.filter(
            empresa=empresa,
            descricao__startswith=f"Compra #{pedido.pk}",
        ).exists()

    def test_gerente_aprova_cotacao(self, client, db):
        empresa = Empresa.objects.create(
            nome="Compras Gerente", cnpj="70.707.070/0001-70", plano="profissional"
        )
        user = User.objects.create_user(username="gerente_compras", password="password")
        Perfil.objects.create(
            usuario=user,
            empresa=empresa,
            data_admissao=date.today(),
            permissao="gerente",
        )
        pedido = PedidoCompra.objects.create(empresa=empresa)
        fornecedor = Fornecedor.objects.create(empresa=empresa, nome="Fornecedor Gerente")
        cotacao = Cotacao.objects.create(
            pedido_compra=pedido,
            fornecedor=fornecedor,
            valor_total="120.00",
            prazo_entrega_dias=4,
        )
        client.login(username="gerente_compras", password="password")

        response = client.post(
            reverse("compras:pedido_detail", kwargs={"pk": pedido.pk}),
            {"aprovar_cotacao": cotacao.pk},
        )

        assert response.status_code == 302
        pedido.refresh_from_db()
        cotacao.refresh_from_db()
        assert pedido.status == "APROVADO"
        assert cotacao.vencedor is True

    def test_almoxarife_recebe_mercadoria(self, client, db):
        empresa = Empresa.objects.create(
            nome="Compras Almoxarife", cnpj="80.808.080/0001-80", plano="profissional"
        )
        user = User.objects.create_user(username="almox_compras", password="password")
        Perfil.objects.create(
            usuario=user,
            empresa=empresa,
            data_admissao=date.today(),
            permissao="almoxarife",
        )
        pedido = PedidoCompra.objects.create(empresa=empresa, status="APROVADO")
        client.login(username="almox_compras", password="password")

        response = client.post(
            reverse("compras:pedido_detail", kwargs={"pk": pedido.pk}),
            {"receber_mercadoria": "1"},
        )

        assert response.status_code == 302
        pedido.refresh_from_db()
        assert pedido.status == "RECEBIDO"
        assert Transacao.objects.filter(
            empresa=empresa,
            descricao__startswith=f"Compra #{pedido.pk}",
        ).count() == 1

    def test_post_com_multiplas_acoes_nao_aprova_nem_recebe_pedido(self, client, db):
        empresa = Empresa.objects.create(
            nome="Compras Ação Única", cnpj="90.909.090/0001-90", plano="profissional"
        )
        user = User.objects.create_user(username="admin_acao_unica", password="password")
        Perfil.objects.create(
            usuario=user,
            empresa=empresa,
            data_admissao=date.today(),
            permissao="admin",
        )
        pedido = PedidoCompra.objects.create(empresa=empresa, status="COTACAO")
        fornecedor = Fornecedor.objects.create(empresa=empresa, nome="Fornecedor Ação Única")
        cotacao = Cotacao.objects.create(
            pedido_compra=pedido,
            fornecedor=fornecedor,
            valor_total="130.00",
            prazo_entrega_dias=3,
        )
        client.login(username="admin_acao_unica", password="password")

        response = client.post(
            reverse("compras:pedido_detail", kwargs={"pk": pedido.pk}),
            {
                "aprovar_cotacao": cotacao.pk,
                "receber_mercadoria": "1",
            },
        )

        assert response.status_code == 400
        pedido.refresh_from_db()
        cotacao.refresh_from_db()
        assert pedido.status == "COTACAO"
        assert cotacao.vencedor is False
        assert not Transacao.objects.filter(
            empresa=empresa,
            descricao__startswith=f"Compra #{pedido.pk}",
        ).exists()

    def test_cotacao_invalida_nao_remove_vencedor_atual(self, client, db):
        empresa = Empresa.objects.create(
            nome="Compras Vencedor", cnpj="11.212.121/0001-11", plano="profissional"
        )
        user = User.objects.create_user(username="gerente_vencedor", password="password")
        Perfil.objects.create(
            usuario=user,
            empresa=empresa,
            data_admissao=date.today(),
            permissao="gerente",
        )
        pedido = PedidoCompra.objects.create(empresa=empresa, status="APROVADO")
        fornecedor = Fornecedor.objects.create(empresa=empresa, nome="Fornecedor Vencedor")
        vencedor = Cotacao.objects.create(
            pedido_compra=pedido,
            fornecedor=fornecedor,
            valor_total="140.00",
            prazo_entrega_dias=2,
            vencedor=True,
        )
        client.login(username="gerente_vencedor", password="password")

        response = client.post(
            reverse("compras:pedido_detail", kwargs={"pk": pedido.pk}),
            {"aprovar_cotacao": 999999},
        )

        assert response.status_code == 404
        pedido.refresh_from_db()
        vencedor.refresh_from_db()
        assert pedido.status == "APROVADO"
        assert vencedor.vencedor is True

    def test_aprovar_vazio_com_recebimento_e_rejeitado_sem_efeitos(self, client, db):
        empresa = Empresa.objects.create(
            nome="Compras Chave Vazia", cnpj="12.313.131/0001-12", plano="profissional"
        )
        user = User.objects.create_user(username="admin_chave_vazia", password="password")
        Perfil.objects.create(
            usuario=user,
            empresa=empresa,
            data_admissao=date.today(),
            permissao="admin",
        )
        pedido = PedidoCompra.objects.create(empresa=empresa, status="APROVADO")
        client.login(username="admin_chave_vazia", password="password")

        response = client.post(
            reverse("compras:pedido_detail", kwargs={"pk": pedido.pk}),
            {"aprovar_cotacao": "", "receber_mercadoria": "1"},
        )

        assert response.status_code == 400
        pedido.refresh_from_db()
        assert pedido.status == "APROVADO"
        assert not Transacao.objects.filter(
            empresa=empresa,
            descricao__startswith=f"Compra #{pedido.pk}",
        ).exists()

    def test_banco_impede_duas_cotacoes_vencedoras_no_mesmo_pedido(self, db):
        empresa = Empresa.objects.create(
            nome="Compras Único Vencedor", cnpj="13.414.141/0001-13", plano="profissional"
        )
        pedido = PedidoCompra.objects.create(empresa=empresa, status="APROVADO")
        fornecedor_a = Fornecedor.objects.create(empresa=empresa, nome="Fornecedor Único A")
        fornecedor_b = Fornecedor.objects.create(empresa=empresa, nome="Fornecedor Único B")
        Cotacao.objects.create(
            pedido_compra=pedido,
            fornecedor=fornecedor_a,
            valor_total="100.00",
            prazo_entrega_dias=2,
            vencedor=True,
        )

        with pytest.raises(IntegrityError):
            with transaction.atomic():
                Cotacao.objects.create(
                    pedido_compra=pedido,
                    fornecedor=fornecedor_b,
                    valor_total="110.00",
                    prazo_entrega_dias=3,
                    vencedor=True,
                )

    @pytest.mark.parametrize(
        ('username', 'perfil_kwargs', 'user_kwargs'),
        [
            ('compras_sem_perfil', None, {}),
            ('compras_perfil_inativo', {'permissao': 'admin', 'ativo': False}, {}),
            ('compras_staff_sem_papel', {'permissao': 'vendedor'}, {'is_staff': True}),
        ],
    )
    def test_principal_sem_papel_ativo_nao_aprova_cotacao(
        self, client, db, username, perfil_kwargs, user_kwargs
    ):
        empresa = Empresa.objects.create(
            nome=f"Empresa {username}", cnpj={
                'compras_sem_perfil': '14.515.151/0001-14',
                'compras_perfil_inativo': '15.616.161/0001-15',
                'compras_staff_sem_papel': '16.717.171/0001-16',
            }[username], plano="profissional"
        )
        user = User.objects.create_user(username=username, password="password", **user_kwargs)
        if perfil_kwargs is not None:
            Perfil.objects.create(
                usuario=user,
                empresa=empresa,
                data_admissao=date.today(),
                **perfil_kwargs,
            )
        pedido = PedidoCompra.objects.create(empresa=empresa)
        fornecedor = Fornecedor.objects.create(empresa=empresa, nome=f"Fornecedor {username}")
        cotacao = Cotacao.objects.create(
            pedido_compra=pedido,
            fornecedor=fornecedor,
            valor_total="150.00",
            prazo_entrega_dias=2,
        )
        client.login(username=username, password="password")

        response = client.post(
            reverse("compras:pedido_detail", kwargs={"pk": pedido.pk}),
            {"aprovar_cotacao": cotacao.pk},
        )

        assert response.status_code in {403, 404}
        pedido.refresh_from_db()
        cotacao.refresh_from_db()
        assert pedido.status == "SOLICITADO"
        assert cotacao.vencedor is False

    def test_superusuario_com_empresa_aprova_cotacao_mesmo_com_perfil_inativo(self, client, db):
        empresa = Empresa.objects.create(
            nome="Compras Superuser", cnpj="17.818.181/0001-17", plano="profissional"
        )
        user = User.objects.create_superuser(
            username="superuser_compras",
            password="password",
            email="superuser@example.com",
        )
        Perfil.objects.create(
            usuario=user,
            empresa=empresa,
            data_admissao=date.today(),
            permissao="vendedor",
            ativo=False,
        )
        pedido = PedidoCompra.objects.create(empresa=empresa)
        fornecedor = Fornecedor.objects.create(empresa=empresa, nome="Fornecedor Superuser")
        cotacao = Cotacao.objects.create(
            pedido_compra=pedido,
            fornecedor=fornecedor,
            valor_total="160.00",
            prazo_entrega_dias=1,
        )
        client.login(username="superuser_compras", password="password")

        response = client.post(
            reverse("compras:pedido_detail", kwargs={"pk": pedido.pk}),
            {"aprovar_cotacao": cotacao.pk},
        )

        assert response.status_code == 302
        pedido.refresh_from_db()
        cotacao.refresh_from_db()
        assert pedido.status == "APROVADO"
        assert cotacao.vencedor is True

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
