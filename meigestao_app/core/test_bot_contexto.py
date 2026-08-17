"""Testes de segurança e comportamento do endpoint `bot_contexto`.

O endpoint alimenta o assistente de IA (chatbot) com dados reais e agregados
da empresa do usuário autenticado. A regra de ouro: ISOLAMENTO — o usuário de
uma empresa jamais pode ver agregados de outra empresa.
"""

from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

from meigestao_app.clientes.models import Cliente
from meigestao_app.core.models import Empresa
from meigestao_app.usuarios.models import Perfil
from meigestao_app.vendas.models import Venda


@pytest.fixture
def empresas_e_usuarios(db):
    emp_a = Empresa.objects.create(nome="Empresa A", cnpj="11.111.111/0001-11")
    emp_b = Empresa.objects.create(nome="Empresa B", cnpj="22.222.222/0001-22")

    user_a = User.objects.create_user(username="cliente_a", password="senha-forte-teste")
    user_b = User.objects.create_user(username="cliente_b", password="senha-forte-teste")
    Perfil.objects.create(usuario=user_a, empresa=emp_a, data_admissao=date.today())
    Perfil.objects.create(usuario=user_b, empresa=emp_b, data_admissao=date.today())

    cliente = Cliente.objects.create(empresa=emp_a, nome="Cliente A", email="a@a.com")
    # Venda confirmada de 100,00 na empresa A, dentro do mês.
    Venda.objects.create(
        empresa=emp_a,
        cliente=cliente,
        status="confirmada",
        valor_total=Decimal("100.00"),
        data_venda=timezone.now(),
    )
    return emp_a, emp_b, user_a, user_b


@pytest.mark.django_db
def test_anonimo_nao_acessa_dados(client):
    response = client.get(reverse("core:bot_contexto"))
    # Sem autenticação: redireciona para login (302) ou 403. Nunca 200 com dados.
    assert response.status_code in (302, 403)


@pytest.mark.django_db
def test_usuario_ve_somente_agregados_da_propria_empresa(client, empresas_e_usuarios):
    emp_a, emp_b, user_a, _user_b = empresas_e_usuarios

    # Venda de 50,00 na empresa B: NÃO deve aparecer para o usuário A.
    cliente_b = Cliente.objects.create(empresa=emp_b, nome="Cliente B", cpf_cnpj="999.999.999-99", email="b@b.com")
    Venda.objects.create(
        empresa=emp_b,
        cliente=cliente_b,
        status="confirmada",
        valor_total=Decimal("5000.00"),
        data_venda=timezone.now(),
    )

    client.force_login(user_a)
    response = client.get(reverse("core:bot_contexto"))

    assert response.status_code == 200
    dados = response.json()
    assert dados["empresa"] == "Empresa A"
    assert dados["faturamento_mes"] == 100.00
    assert dados["faturamento_hoje"] == 100.00
    assert dados["total_vendas_mes"] == 1
    assert dados["vendas_pendentes"] == 0
    # Garante que a venda da empresa B (5000) não vazou de nenhuma forma.
    assert dados["faturamento_mes"] != 5100.00


@pytest.mark.django_db
def test_usuario_sem_empresa_recebe_403(client, empresas_e_usuarios):
    _emp_a, _emp_b, _user_a, user_sem = empresas_e_usuarios
    # Cria um usuário sem Perfil/empresa vinculada.
    sem_empresa = User.objects.create_user(
        username="sem_empresa", password="senha-forte-teste"
    )
    client.force_login(sem_empresa)
    response = client.get(reverse("core:bot_contexto"))
    assert response.status_code == 403
