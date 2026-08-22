# -*- coding: utf-8 -*-
"""Critérios de aceite da Spec do Painel Executivo em Modo Demonstração (/demo/)."""
from decimal import Decimal

import pytest
from django.core.management import call_command
from django.urls import reverse

from meigestao_app.clientes.models import Cliente
from meigestao_app.core.demo_data import DEMO_CNPJ, seed_demo_db
from meigestao_app.core.models import Empresa


@pytest.fixture(autouse=True)
def _limpa_demo(db):
    Empresa.objects.filter(cnpj=DEMO_CNPJ).delete()


def test_ca1_get_demo_anônimo_renderiza(client, db):
    resp = client.get(reverse('demo'))
    assert resp.status_code == 200
    corpo = resp.content.decode()
    assert 'Demonstração' in corpo
    assert 'Faturamento do mês' in corpo
    assert 'Estoque baixo' in corpo


def test_ca1_get_demo_sem_login_nao_redireciona(client, db):
    # pública: não deve redirecionar para login
    resp = client.get('/demo/')
    assert resp.status_code == 200
    assert 'demo/' not in (resp.headers.get('Location') or '')


def test_ca2_demo_nao_vaza_dados_de_empresa_real(client, db):
    # uma empresa REAL com nome marcante NÃO pode aparecer no demo
    real = Empresa.objects.create(nome='SEGREDO-TESTE-XYZ', cnpj='11.111.111/0001-11')
    Cliente.objects.create(empresa=real, nome='Cliente Secreto SA', cpf_cnpj='99.999.999/0001-99')
    resp = client.get(reverse('demo'))
    corpo = resp.content.decode()
    assert 'SEGREDO-TESTE-XYZ' not in corpo
    assert 'Cliente Secreto SA' not in corpo


def test_ca3_seed_idempotente(db):
    primeiro_empresas = Empresa.objects.filter(cnpj=DEMO_CNPJ).count()
    seed_demo_db()
    seed_demo_db()          # rodar de novo não duplica
    assert Empresa.objects.filter(cnpj=DEMO_CNPJ).count() == primeiro_empresas + 1


def test_ca3_comando_seed_demo_roda(db):
    Empresa.objects.filter(cnpj=DEMO_CNPJ).delete()
    call_command('seed_demo')
    assert Empresa.objects.filter(cnpj=DEMO_CNPJ).exists()


def test_ca4_demo_tem_dados_e_faturamento_positivo(client, db):
    resp = client.get(reverse('demo'))
    # corpore: usa a query do mês; garantimos vendas no mês corrente via seed
    ctx = resp.context
    assert ctx['faturamento_mes'] > 0
    assert ctx['total_vendas_mes'] > 0


def test_ca5_cta_aponta_para_cadastro(client, db):
    resp = client.get(reverse('demo'))
    assert '/cadastro/' in resp.content.decode()


def test_ca_demo_totalmente_isolado(db):
    # dados demo NUNCA criam venda fora da empresa demo
    seed_demo_db()
    demo = Empresa.objects.get(cnpj=DEMO_CNPJ)
    outras = Empresa.objects.exclude(pk=demo.pk).count()
    assert outras == 0
