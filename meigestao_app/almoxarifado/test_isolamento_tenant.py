from datetime import date

import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from meigestao_app.almoxarifado.models import (
    EnderecoArmazenamento,
    LocalArmazenamento,
    RequisicaoInterna,
    Setor,
)
from meigestao_app.core.models import Empresa
from meigestao_app.usuarios.models import Perfil


@pytest.fixture
def empresas_com_usuario_e_almoxarifado(db):
    empresa_a = Empresa.objects.create(
        nome="Almox A",
        cnpj="51.111.111/0001-51",
        plano="profissional",
    )
    empresa_b = Empresa.objects.create(
        nome="Almox B",
        cnpj="52.222.222/0001-52",
        plano="profissional",
    )
    usuario_a = User.objects.create_user(
        username="almox_a",
        password="senha-forte-de-teste",
    )
    Perfil.objects.create(
        usuario=usuario_a,
        empresa=empresa_a,
        data_admissao=date.today(),
        permissao="admin",
    )
    solicitante_b = User.objects.create_user(
        username="solicitante_b",
        password="senha-forte-de-teste",
    )
    Perfil.objects.create(
        usuario=solicitante_b,
        empresa=empresa_b,
        data_admissao=date.today(),
    )
    setor_b = Setor.objects.create(empresa=empresa_b, nome="Setor B")
    local_b = LocalArmazenamento.objects.create(
        empresa=empresa_b,
        nome="Depósito B",
    )
    endereco_b = EnderecoArmazenamento.objects.create(
        local=local_b,
        codigo_endereco="B-PRAT-01",
    )
    requisicao_b = RequisicaoInterna.objects.create(
        empresa=empresa_b,
        solicitante=solicitante_b,
        setor=setor_b,
        local_origem=local_b,
        justificativa="Exclusiva da Empresa B",
    )
    return usuario_a, setor_b, endereco_b, requisicao_b


@pytest.mark.django_db
class TestIsolamentoAlmoxarifadoEntreEmpresas:
    def test_formulario_requisicao_filtra_setor_e_local_por_empresa(
        self, client, empresas_com_usuario_e_almoxarifado
    ):
        usuario_a, setor_b, _, requisicao_b = empresas_com_usuario_e_almoxarifado
        empresa_a = usuario_a.perfil.empresa
        setor_a = Setor.objects.create(empresa=empresa_a, nome="Setor A")
        local_a = LocalArmazenamento.objects.create(
            empresa=empresa_a,
            nome="Depósito A",
        )
        client.force_login(usuario_a)

        response = client.get(reverse("almoxarifado:requisicao_create"))

        assert response.status_code == 200
        form = response.context["form"]
        assert setor_a in form.fields["setor"].queryset
        assert setor_b not in form.fields["setor"].queryset
        assert local_a in form.fields["local_origem"].queryset
        assert requisicao_b.local_origem not in form.fields["local_origem"].queryset

    def test_post_nao_cria_requisicao_com_setor_e_local_de_outra_empresa(
        self, client, empresas_com_usuario_e_almoxarifado
    ):
        usuario_a, setor_b, _, requisicao_b = empresas_com_usuario_e_almoxarifado
        client.force_login(usuario_a)

        response = client.post(
            reverse("almoxarifado:requisicao_create"),
            {
                "setor": setor_b.pk,
                "local_origem": requisicao_b.local_origem_id,
                "justificativa": "Tentativa cross-tenant",
            },
        )

        assert response.status_code == 200
        assert not RequisicaoInterna.objects.filter(
            empresa=usuario_a.perfil.empresa,
            justificativa="Tentativa cross-tenant",
        ).exists()
        form = response.context["form"]
        assert "setor" in form.errors
        assert "local_origem" in form.errors

    def test_formulario_endereco_nao_lista_local_de_outra_empresa(
        self, client, empresas_com_usuario_e_almoxarifado
    ):
        usuario_a, _, endereco_b, _ = empresas_com_usuario_e_almoxarifado
        local_a = LocalArmazenamento.objects.create(
            empresa=usuario_a.perfil.empresa,
            nome="Depósito A",
        )
        client.force_login(usuario_a)

        response = client.get(reverse("almoxarifado:endereco_create"))

        assert response.status_code == 200
        queryset = response.context["form"].fields["local"].queryset
        assert local_a in queryset
        assert endereco_b.local not in queryset

    def test_formulario_setor_nao_lista_responsavel_de_outra_empresa(
        self, client, empresas_com_usuario_e_almoxarifado
    ):
        usuario_a, _, _, requisicao_b = empresas_com_usuario_e_almoxarifado
        client.force_login(usuario_a)

        response = client.get(reverse("almoxarifado:setor_create"))

        assert response.status_code == 200
        queryset = response.context["form"].fields["responsavel"].queryset
        assert usuario_a in queryset
        assert requisicao_b.solicitante not in queryset

    def test_lista_nao_exibe_requisicao_de_outra_empresa(
        self, client, empresas_com_usuario_e_almoxarifado
    ):
        usuario_a, _, _, requisicao_b = empresas_com_usuario_e_almoxarifado
        client.force_login(usuario_a)

        response = client.get(reverse("almoxarifado:requisicao_list"))

        assert response.status_code == 200
        assert requisicao_b not in response.context["requisicoes"]

    def test_usuario_nao_visualiza_requisicao_de_outra_empresa(
        self, client, empresas_com_usuario_e_almoxarifado
    ):
        usuario_a, _, _, requisicao_b = empresas_com_usuario_e_almoxarifado
        client.force_login(usuario_a)

        response = client.get(
            reverse("almoxarifado:requisicao_detail", kwargs={"pk": requisicao_b.pk})
        )

        assert response.status_code == 404

    def test_usuario_nao_aprova_requisicao_de_outra_empresa(
        self, client, empresas_com_usuario_e_almoxarifado
    ):
        usuario_a, _, _, requisicao_b = empresas_com_usuario_e_almoxarifado
        client.force_login(usuario_a)

        response = client.post(
            reverse("almoxarifado:requisicao_aprovar", kwargs={"pk": requisicao_b.pk}),
            {"acao": "aprovar"},
        )

        assert response.status_code == 404
        requisicao_b.refresh_from_db()
        assert requisicao_b.status == "SOLICITADO"

    @pytest.mark.parametrize("url_name", ["setor_update", "setor_delete"])
    def test_usuario_nao_abre_setor_de_outra_empresa(
        self, client, empresas_com_usuario_e_almoxarifado, url_name
    ):
        usuario_a, setor_b, _, _ = empresas_com_usuario_e_almoxarifado
        client.force_login(usuario_a)

        response = client.get(
            reverse(f"almoxarifado:{url_name}", kwargs={"pk": setor_b.pk})
        )

        assert response.status_code == 404

    def test_usuario_nao_abre_prateleira_de_outra_empresa(
        self, client, empresas_com_usuario_e_almoxarifado
    ):
        usuario_a, _, endereco_b, _ = empresas_com_usuario_e_almoxarifado
        client.force_login(usuario_a)

        response = client.get(
            reverse(
                "almoxarifado:prateleira_view",
                kwargs={"codigo": endereco_b.codigo_endereco},
            )
        )

        assert response.status_code == 404
