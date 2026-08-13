from datetime import date

import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from meigestao_app.core.models import Empresa
from meigestao_app.usuarios.models import Perfil


@pytest.mark.django_db
def test_lista_de_usuarios_exibe_somente_perfis_da_propria_empresa(client):
    empresa_a = Empresa.objects.create(
        nome="Usuários A",
        cnpj="71.111.111/0001-71",
    )
    empresa_b = Empresa.objects.create(
        nome="Usuários B",
        cnpj="72.222.222/0001-72",
    )
    usuario_a = User.objects.create_user(
        username="usuario_lista_a",
        password="senha-forte-de-teste",
    )
    perfil_a = Perfil.objects.create(
        usuario=usuario_a,
        empresa=empresa_a,
        data_admissao=date.today(),
        permissao="admin",
    )
    usuario_b = User.objects.create_user(
        username="usuario_lista_b",
        password="senha-forte-de-teste",
    )
    perfil_b = Perfil.objects.create(
        usuario=usuario_b,
        empresa=empresa_b,
        data_admissao=date.today(),
    )
    client.force_login(usuario_a)

    response = client.get(reverse("usuarios:usuario_list"))

    assert response.status_code == 200
    assert perfil_a in response.context["usuarios"]
    assert perfil_b not in response.context["usuarios"]
