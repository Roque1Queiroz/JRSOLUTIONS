from datetime import date

import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from meigestao_app.core.models import Empresa, Lembrete
from meigestao_app.usuarios.models import Perfil


@pytest.fixture
def usuarios_com_lembrete_de_outra_empresa(db):
    empresa_a = Empresa.objects.create(nome="Lembretes A", cnpj="81.111.111/0001-81")
    empresa_b = Empresa.objects.create(nome="Lembretes B", cnpj="82.222.222/0001-82")
    usuario_a = User.objects.create_user(
        username="lembrete_a", password="senha-forte-de-teste"
    )
    Perfil.objects.create(
        usuario=usuario_a,
        empresa=empresa_a,
        data_admissao=date.today(),
    )
    usuario_b = User.objects.create_user(
        username="lembrete_b", password="senha-forte-de-teste"
    )
    Perfil.objects.create(
        usuario=usuario_b,
        empresa=empresa_b,
        data_admissao=date.today(),
    )
    lembrete_b = Lembrete.objects.create(
        empresa=empresa_b,
        usuario=usuario_b,
        titulo="Lembrete exclusivo da B",
        conteudo="Conteúdo privado",
    )
    return usuario_a, lembrete_b


@pytest.mark.django_db
class TestIsolamentoLembretes:
    def test_usuario_nao_alterna_lembrete_de_outro_usuario(
        self, client, usuarios_com_lembrete_de_outra_empresa
    ):
        usuario_a, lembrete_b = usuarios_com_lembrete_de_outra_empresa
        client.force_login(usuario_a)

        response = client.post(
            reverse("core:lembrete_concluir", kwargs={"pk": lembrete_b.pk})
        )

        assert response.status_code == 404
        lembrete_b.refresh_from_db()
        assert lembrete_b.concluido is False

    def test_usuario_nao_exclui_lembrete_de_outro_usuario(
        self, client, usuarios_com_lembrete_de_outra_empresa
    ):
        usuario_a, lembrete_b = usuarios_com_lembrete_de_outra_empresa
        client.force_login(usuario_a)

        response = client.post(
            reverse("core:lembrete_excluir", kwargs={"pk": lembrete_b.pk})
        )

        assert response.status_code == 404
        assert Lembrete.objects.filter(pk=lembrete_b.pk).exists()
