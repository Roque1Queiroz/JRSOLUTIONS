# -*- coding: utf-8 -*-
"""Testes das páginas públicas legais (Política de Privacidade LGPD e Termos de Uso)."""
import pytest
from django.urls import reverse


def test_privacidade_renderiza(client, db):
    resp = client.get(reverse('core:privacidade'))
    assert resp.status_code == 200
    corpo = resp.content.decode()
    assert 'Política de Privacidade' in corpo
    assert 'LGPD' in corpo
    assert 'controlador' in corpo
    assert 'art. 18' in corpo or 'art. 7' in corpo  # direitos do titular / bases legais


def test_privacidade_alias_raiz(client, db):
    # alias público /privacidade/ (usado pela landing e rodapés)
    resp = client.get('/privacidade/')
    assert resp.status_code == 200
    assert 'LGPD' in resp.content.decode()


def test_termos_renderiza(client, db):
    resp = client.get(reverse('core:termos'))
    assert resp.status_code == 200
    corpo = resp.content.decode()
    assert 'Termos de Uso' in corpo
    assert 'LGPD' in corpo
    assert 'multi-tenant' in corpo or 'suspensão' in corpo or 'responsabilidades' in corpo.lower()


def test_termos_alias_raiz(client, db):
    resp = client.get('/termos/')
    assert resp.status_code == 200


def test_paginas_publicas_sem_login(client, db):
    # devem ser acessíveis SEM autenticação (não redirecionam para login)
    for url in ['/privacidade/', '/termos/', reverse('core:privacidade'), reverse('core:termos')]:
        resp = client.get(url)
        assert resp.status_code == 200, url


def test_cadastro_referencia_termos_e_privacidade(client, db):
    resp = client.get(reverse('core:cadastro'))
    corpo = resp.content.decode()
    assert '/termos/' in corpo
    assert '/privacidade/' in corpo


def test_login_referencia_termos_e_privacidade(client, db):
    resp = client.get(reverse('core:login'))
    corpo = resp.content.decode()
    assert 'Termos de Uso' in corpo
    assert 'Privacidade' in corpo
