# -*- coding: utf-8 -*-
"""Testes do login público do cliente (substitui a tela do admin na rotina normal)."""
import datetime

import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from meigestao_app.core.models import Empresa
from meigestao_app.usuarios.models import Perfil


@pytest.fixture
def empresa(db):
    e = Empresa.objects.create(nome='Loja Login ME', cnpj='11.222.333/0001-44')
    e.iniciar_teste()
    return e


@pytest.fixture
def usuario(db, empresa):
    u = User.objects.create_user(
        username='cliente@login.com.br', email='cliente@login.com.br',
        password='senha-forte-123',
    )
    Perfil.objects.create(
        usuario=u, empresa=empresa, permissao='admin',
        data_admissao=datetime.date.today(), ativo=True,
    )
    return u


def test_get_login_renderiza_painel(client, db):
    resp = client.get(reverse('core:login'))
    assert resp.status_code == 200
    corpo = resp.content.decode()
    assert 'Entrar' in corpo
    assert 'SISTEMA GESTOR' in corpo


def test_raiz_redireciona_para_login_publico(client, db):
    # Raiz protegida: sem login -> vai para o login público (nao mais admin).
    resp = client.get(reverse('core:dashboard'))
    assert resp.status_code == 302
    assert reverse('core:login') in resp.headers['Location']
    assert '/admin/login' not in resp.headers['Location']


def test_login_valido_autentica_e_vai_ao_dashboard(client, db, usuario):
    resp = client.post(reverse('core:login'), {
        'username': 'cliente@login.com.br', 'password': 'senha-forte-123',
    })
    assert resp.status_code == 302
    assert '_auth_user_id' in client.session
    assert resp.headers['Location'] == reverse('core:dashboard')


def test_login_senha_errada(client, db, usuario):
    resp = client.post(reverse('core:login'), {
        'username': 'cliente@login.com.br', 'password': 'senha-errada',
    })
    # Refaz a tela de login sem autenticar (mensagem de erro pt-BR do Django).
    assert resp.status_code == 200
    assert '_auth_user_id' not in client.session
    corpo = resp.content.decode()
    assert 'senha' in corpo.lower() or 'usu\u00e1rio' in corpo.lower()


def test_login_preserva_next(client, db, usuario):
    resp = client.post(reverse('core:login') + '?next=/vendas/', {
        'username': 'cliente@login.com.br', 'password': 'senha-forte-123',
    })
    assert resp.status_code == 302
    assert resp.headers['Location'] == '/vendas/'


def test_login_ignora_next_externo(client, db, usuario):
    # Open-redirect: next apontando pra fora cai no dashboard (seguro).
    resp = client.post(reverse('core:login') + '?next=https://evil.com', {
        'username': 'cliente@login.com.br', 'password': 'senha-forte-123',
    })
    assert resp.status_code == 302
    assert resp.headers['Location'] == reverse('core:dashboard')


def test_logout_encerra_sessao(client, db, usuario):
    client.force_login(usuario)
    resp = client.get(reverse('core:logout'))
    assert resp.status_code == 302
    assert resp.headers['Location'] == reverse('core:login')
    assert '_auth_user_id' not in client.session
