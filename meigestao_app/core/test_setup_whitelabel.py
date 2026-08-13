import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from meigestao_app.core.models import Empresa


@pytest.mark.django_db
def test_setup_sem_perfil_nao_edita_primeira_empresa(client):
    empresa_existente = Empresa.objects.create(
        nome="Empresa protegida",
        cnpj="93.333.333/0001-93",
    )
    usuario = User.objects.create_user(
        username="setup_sem_perfil",
        password="senha-forte-de-teste",
    )
    client.force_login(usuario)

    response = client.post(
        reverse("core:setup_whitelabel"),
        {
            "nome": "Empresa sequestrada",
            "cnpj": "94.444.444/0001-94",
        },
    )

    assert response.status_code in (302, 403, 404)
    empresa_existente.refresh_from_db()
    assert empresa_existente.nome == "Empresa protegida"
    assert not Empresa.objects.filter(nome="Empresa sequestrada").exists()
