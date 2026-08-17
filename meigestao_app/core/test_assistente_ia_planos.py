"""Regressão: o assistente de IA (chatbot) é exibido em TODOS os planos.

Decisão de 17/08/2026: retirado o guard `{% if empresa_obj.plano != 'basico' %}`
que ocultava o widget do chat no plano Básico/MEI. O widget deve aparecer no
HTML servido para qualquer usuário autenticado, de qualquer plano.
"""

from datetime import date

import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from meigestao_app.core.models import Empresa
from meigestao_app.usuarios.models import Perfil


@pytest.fixture
def empresa_plano(plano):
    return Empresa.objects.create(nome=f"Empresa {plano}", cnpj="71.111.111/0001-71", plano=plano)


@pytest.fixture
def usuario_logado(client, empresa_plano):
    usuario = User.objects.create_user(username="cli_basico", password="senha-forte-de-teste")
    Perfil.objects.create(usuario=usuario, empresa=empresa_plano, data_admissao=date.today())
    client.force_login(usuario)
    return usuario, empresa_plano


@pytest.mark.parametrize("plano", ["basico", "profissional", "enterprise"])
@pytest.mark.django_db
def test_widget_assistente_ia_presente_em_todos_os_planos(client, usuario_logado, plano):
    _usuario, _empresa = usuario_logado
    response = client.get(reverse("core:dashboard"))

    assert response.status_code == 200
    html = response.content.decode()
    assert 'id="chatbot-widget"' in html, f"widget do chat ausente no plano {plano}"
    assert "API_URL" in html, f"script do chat ausente no plano {plano}"
