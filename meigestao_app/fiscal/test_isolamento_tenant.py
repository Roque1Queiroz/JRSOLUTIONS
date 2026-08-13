from datetime import date

import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from meigestao_app.clientes.models import Cliente
from meigestao_app.core.models import Empresa
from meigestao_app.fiscal.models import NotaFiscal
from meigestao_app.usuarios.models import Perfil
from meigestao_app.vendas.models import Venda


@pytest.fixture
def empresas_com_usuario_e_notas(db):
    empresa_a = Empresa.objects.create(
        nome="Fiscal A",
        cnpj="31.111.111/0001-31",
        plano="profissional",
    )
    empresa_b = Empresa.objects.create(
        nome="Fiscal B",
        cnpj="32.222.222/0001-32",
    )
    usuario_a = User.objects.create_user(
        username="fiscal_a",
        password="senha-forte-de-teste",
    )
    Perfil.objects.create(
        usuario=usuario_a,
        empresa=empresa_a,
        data_admissao=date.today(),
        permissao="admin",
    )
    cliente_a = Cliente.objects.create(
        empresa=empresa_a,
        nome="Cliente A",
        cpf_cnpj="311.111.111-31",
    )
    cliente_b = Cliente.objects.create(
        empresa=empresa_b,
        nome="Cliente B",
        cpf_cnpj="322.222.222-32",
    )
    venda_b = Venda.objects.create(
        empresa=empresa_b,
        cliente=cliente_b,
        valor_subtotal="100.00",
        valor_total="100.00",
    )
    nota_b = NotaFiscal.objects.create(
        empresa=empresa_b,
        cliente=cliente_b,
        venda=venda_b,
        numero="NF-B-001",
        valor_subtotal="100.00",
    )
    return usuario_a, empresa_a, empresa_b, cliente_a, cliente_b, venda_b, nota_b


@pytest.mark.django_db
class TestIsolamentoFiscalEntreEmpresas:
    @pytest.mark.parametrize(
        "url_name",
        [
            "fiscal:nota_fiscal_detail",
            "fiscal:nota_fiscal_update",
            "fiscal:nota_fiscal_delete",
            "fiscal:nota_fiscal_pdf",
        ],
    )
    def test_usuario_nao_abre_nota_de_outra_empresa(
        self, client, empresas_com_usuario_e_notas, url_name
    ):
        usuario_a, *_, nota_b = empresas_com_usuario_e_notas
        client.force_login(usuario_a)

        response = client.get(reverse(url_name, kwargs={"pk": nota_b.pk}))

        assert response.status_code == 404

    def test_usuario_nao_exclui_nota_de_outra_empresa(
        self, client, empresas_com_usuario_e_notas
    ):
        usuario_a, *_, nota_b = empresas_com_usuario_e_notas
        client.force_login(usuario_a)

        response = client.post(
            reverse("fiscal:nota_fiscal_delete", kwargs={"pk": nota_b.pk})
        )

        assert response.status_code == 404
        assert NotaFiscal.objects.filter(pk=nota_b.pk).exists()

    def test_formulario_de_nota_lista_apenas_relacoes_da_empresa_do_usuario(
        self, client, empresas_com_usuario_e_notas
    ):
        (
            usuario_a,
            empresa_a,
            empresa_b,
            cliente_a,
            cliente_b,
            venda_b,
            _,
        ) = empresas_com_usuario_e_notas
        client.force_login(usuario_a)

        response = client.get(reverse("fiscal:nota_fiscal_create"))

        assert response.status_code == 200
        form = response.context["form"]
        assert list(form.fields["empresa"].queryset) == [empresa_a]
        assert cliente_a in form.fields["cliente"].queryset
        assert cliente_b not in form.fields["cliente"].queryset
        assert venda_b not in form.fields["venda"].queryset
        assert empresa_b not in form.fields["empresa"].queryset

    def test_usuario_nao_inicializa_nota_com_venda_de_outra_empresa(
        self, client, empresas_com_usuario_e_notas
    ):
        usuario_a, _, _, _, cliente_b, venda_b, _ = empresas_com_usuario_e_notas
        client.force_login(usuario_a)

        response = client.get(
            reverse(
                "fiscal:nota_fiscal_create_from_venda",
                kwargs={"venda_id": venda_b.pk},
            )
        )

        assert response.status_code == 404
        assert response.context is None or response.context.get("form") is None
