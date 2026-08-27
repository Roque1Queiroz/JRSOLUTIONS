# -*- coding: utf-8 -*-
"""Testes do cadastro self-service (landing): cria Empresa + usuário admin + 30 dias de trial."""
import datetime

import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from meigestao_app.core.models import Empresa
from meigestao_app.usuarios.models import Perfil


# CNPJs e CPFs VÁLIDOS (dígitos verificadores reais) — usados para respeitar a
# validação de documentos adicionada na auditoria de segurança (2026-08-27).
CNPJ_BASE = '30.883.224/4935-98'
CNPJ_DUPLICADO = '22.105.824/5213-04'
CNPJ_DOIS = '12.165.009/4830-00'


def _dados(**over):
    base = {
        'nome_empresa': 'Loja do Teste ME',
        'cnpj': CNPJ_BASE,
        'primeiro_nome': 'Maria',
        'sobrenome': 'Silva',
        'email': 'maria@teste.com.br',
        'senha': 'senha-forte-123',
        'confirma': 'senha-forte-123',
    }
    base.update(over)
    return base


def test_get_cadastro_renderiza_formulario(client, db):
    resp = client.get(reverse('core:cadastro'))
    assert resp.status_code == 200
    corpo = resp.content.decode()
    assert 'Criar conta grátis' in corpo
    assert '30 dias' in corpo


def test_post_cadastro_cria_empresa_usuario_e_trial(client, db):
    resp = client.post(reverse('core:cadastro'), _dados())
    assert resp.status_code in (302, 200)

    empresa = Empresa.objects.filter(cnpj=CNPJ_BASE).first()
    assert empresa is not None
    assert empresa.em_teste is True
    assert empresa.plano == 'enterprise'

    usuario = User.objects.filter(username='maria@teste.com.br').first()
    assert usuario is not None
    perfil = Perfil.objects.filter(usuario=usuario, empresa=empresa).first()
    assert perfil is not None
    assert perfil.permissao == 'admin'
    assert perfil.data_admissao == datetime.date.today()
    assert perfil.ativo is True


def test_post_cadastro_sai_logado(client, db):
    resp = client.post(reverse('core:cadastro'), _dados(), follow=True)
    assert resp.status_code == 200
    # O usuário recém-criado está autenticado e cai no dashboard.
    assert resp.context['user'].is_authenticated
    assert '_auth_user_id' in client.session


def test_post_cadastro_senhas_nao_confere(client, db):
    resp = client.post(reverse('core:cadastro'), _dados(confirma='outra-senha-123'))
    assert resp.status_code == 200
    assert b'confirma' in resp.content.lower() or 'confirma' in resp.content.decode()
    assert not Empresa.objects.filter(cnpj=CNPJ_BASE).exists()


def test_post_cadastro_cnpj_invalido_negado(client, db):
    """CNPJ com dígitos verificadores inválidos deve ser recusado."""
    resp = client.post(reverse('core:cadastro'), _dados(cnpj='12.345.678/0001-90'))
    corpo = resp.content.decode()
    assert resp.status_code == 200
    assert 'CNPJ inválido' in corpo
    assert not Empresa.objects.filter(cnpj='12.345.678/0001-90').exists()


def test_post_cadastro_cnpj_duplicado(client, db):
    Empresa.objects.create(nome='Ja Existe', cnpj=CNPJ_DUPLICADO)
    resp = client.post(reverse('core:cadastro'), _dados(cnpj=CNPJ_DUPLICADO))
    corpo = resp.content.decode()
    assert resp.status_code == 200
    assert 'Já existe uma conta com este CNPJ' in corpo
    assert Empresa.objects.filter(nome='Loja do Teste ME').count() == 0


def test_post_cadastro_email_duplicado(client, db):
    User.objects.create_user(username='maria@teste.com.br', password='x-12345678')
    resp = client.post(reverse('core:cadastro'), _dados())
    corpo = resp.content.decode()
    assert resp.status_code == 200
    assert 'Já existe uma conta com este e-mail' in corpo


def test_post_cadastro_usuario_logado_redireciona(client, db, django_user_model):
    from meigestao_app.core.models import Empresa
    from meigestao_app.usuarios.models import Perfil
    e = Empresa.objects.create(nome='Marcas ME', cnpj=CNPJ_DOIS)
    u = django_user_model.objects.create_user(username='logado@x.com', password='senha-forte')
    Perfil.objects.create(usuario=u, empresa=e, permissao='admin', data_admissao=datetime.date.today())
    client.force_login(u)
    resp = client.get(reverse('core:cadastro'))
    assert resp.status_code == 302
    assert resp.headers.get('Location') == reverse('core:dashboard')