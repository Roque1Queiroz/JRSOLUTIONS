from datetime import date

import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from meigestao_app.core.models import Empresa
from meigestao_app.financeiro.models import RelatorioInteligencia
from meigestao_app.usuarios.models import Perfil


@pytest.fixture
def usuario_com_empresa(db):
    empresa = Empresa.objects.create(nome="Empresa Dashboard", cnpj="71.111.111/0001-71")
    usuario = User.objects.create_user(username="dashboard_user", password="senha-forte-de-teste")
    Perfil.objects.create(usuario=usuario, empresa=empresa, data_admissao=date.today())
    return usuario, empresa


@pytest.mark.django_db
def test_dashboard_mostra_relatorio_persistido_do_dia(client, usuario_com_empresa):
    usuario, empresa = usuario_com_empresa
    dados = {
        "data": date.today().strftime("%d/%m/%Y"),
        "entradas_hoje": 200.0,
        "saidas_hoje": 90.0,
        "projecao": 110.0,
        "status": "ALERTA",
        "mensagem": "Verifique os recebimentos.",
    }
    RelatorioInteligencia.objects.create(
        empresa=empresa, data_referencia=date.today(), dados_json=dados
    )
    client.force_login(usuario)

    response = client.get(reverse("core:dashboard"))

    assert response.status_code == 200
    assert response.context["analise"] == dados


@pytest.mark.django_db
def test_dashboard_calcula_ao_vivo_quando_nao_ha_relatorio_do_dia(
    client, usuario_com_empresa
):
    usuario, _empresa = usuario_com_empresa
    client.force_login(usuario)

    response = client.get(reverse("core:dashboard"))

    assert response.status_code == 200
    analise = response.context["analise"]
    assert analise is not None
    assert analise["status"] == "SUCESSO"
    assert analise["projecao"] == 0.0
