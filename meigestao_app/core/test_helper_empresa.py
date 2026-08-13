import pytest
from django.contrib.auth.models import User

from meigestao_app.core.models import Empresa
from meigestao_app.core.utils.helpers import get_empresa_do_usuario


@pytest.mark.django_db
def test_staff_sem_perfil_nao_recebe_primeira_empresa_implicitamente():
    Empresa.objects.create(nome="Empresa arbitrária", cnpj="95.555.555/0001-95")
    staff = User.objects.create_user(
        username="staff_sem_perfil",
        password="senha-forte-de-teste",
        is_staff=True,
    )

    assert get_empresa_do_usuario(staff) is None
