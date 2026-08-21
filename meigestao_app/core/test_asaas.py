# -*- coding: utf-8 -*-
"""Testes da integração Asaas: cliente, webhook e ação de contratar (mock, sem rede)."""
import datetime
import json
import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from meigestao_app.core import asaas
from meigestao_app.core.models import Empresa
from meigestao_app.usuarios.models import Perfil


@pytest.fixture
def empresa(db):
    e = Empresa.objects.create(nome="Cliente Asaas", cnpj="89.999.999/0001-99")
    e.iniciar_teste(dias=30)
    e.trial_expira_em = e.trial_expira_em - datetime.timedelta(days=31)  # expira
    e.save(update_fields=["trial_expira_em"])
    e.refresh_from_db()
    return e


@pytest.fixture
def cliente_sem_trial(db):
    return Empresa.objects.create(nome="Sem Trial", cnpj="98.888.888/0001-88", plano="basico")


@pytest.fixture
def usuario(client, empresa):
    u = User.objects.create_user(username="cliente_u", password="senha")
    Perfil.objects.create(usuario=u, empresa=empresa, permissao="admin",
                          data_admissao=datetime.date.today())
    client.force_login(u)
    return u


def test_plano_por_valor():
    assert asaas.plano_por_valor(79) == "basico"
    assert asaas.plano_por_valor(199) == "profissional"
    assert asaas.plano_por_valor(499) == "enterprise"
    assert asaas.plano_por_valor(0) is None


def _post_webhook(client, payload):
    return client.post(reverse("core:asaas_webhook"),
                       data=json.dumps(payload), content_type="application/json")


def test_webhook_pagamento_confirmado_converte_plano(client, empresa):
    resp = _post_webhook(client, {
        "event": "PAYMENT_CONFIRMED",
        "payment": {"id": "pay_1", "externalReference": str(empresa.id), "value": 199.0},
    })
    assert resp.status_code == 200
    empresa.refresh_from_db()
    assert empresa.plano == "profissional"
    assert empresa.trial_expira_em is None  # teste encerrado


def test_webhook_subscription_confirmado_converte(client, empresa):
    resp = _post_webhook(client, {
        "event": "SUBSCRIPTION_PAYMENT_CONFIRMED",
        "subscription": {"id": "sub_1", "externalReference": str(empresa.id), "value": 499.0},
    })
    assert resp.status_code == 200
    empresa.refresh_from_db()
    assert empresa.plano == "enterprise"


def test_webhook_tambem_localiza_por_id_assinatura(client, empresa):
    empresa.asaas_subscription_id = "sub_xyz"
    empresa.save(update_fields=["asaas_subscription_id"])
    payload = {"event": "PAYMENT_RECEIVED",
               "subscription": {"id": "sub_xyz", "value": 79.0}}  # sem externalReference
    resp = _post_webhook(client, payload)
    assert resp.status_code == 200
    empresa.refresh_from_db()
    assert empresa.plano == "basico"


def test_webhook_evento_irrelevante_nao_altera(client, empresa):
    resp = _post_webhook(client, {
        "event": "PAYMENT_OVERDUE",
        "payment": {"id": "p", "externalReference": str(empresa.id), "value": 199.0},
    })
    assert resp.status_code == 200
    empresa.refresh_from_db()
    assert empresa.trial_expira_em is not None  # continua em teste expirado


def test_webhook_sem_empresa_404(client, db):
    resp = _post_webhook(client, {
        "event": "PAYMENT_CONFIRMED",
        "payment": {"id": "p", "externalReference": "999999", "value": 199.0},
    })
    assert resp.status_code == 404


def test_webhook_metodo_nao_post_404(client):
    assert client.get(reverse("core:asaas_webhook")).status_code == 404


def test_webhook_json_invalido_400(client):
    resp = client.post(reverse("core:asaas_webhook"), data=b"{invalid",
                       content_type="application/json")
    assert resp.status_code == 400


def test_webhook_token_incorreto_403(client, empresa, settings):
    settings.ASAAS_WEBHOOK_TOKEN = "segredo"
    resp = _post_webhook(client, {
        "event": "PAYMENT_CONFIRMED", "authToken": "errado",
        "payment": {"externalReference": str(empresa.id), "value": 199.0},
    })
    assert resp.status_code == 403


def test_contratar_plano_redireciona_ao_checkout(client, settings, cliente_sem_trial, monkeypatch):
    u = User.objects.create_user(username="comprador", password="senha")
    Perfil.objects.create(usuario=u, empresa=cliente_sem_trial, permissao="admin",
                          data_admissao=datetime.date.today())
    client.force_login(u)
    settings.ASAAS_API_KEY = "aact_teste"
    monkeypatch.setattr(asaas, "criar_assinatura", lambda empresa, plano: {"id": "sub_1"})
    monkeypatch.setattr(asaas, "link_de_pagamento", lambda sid: "https://pay.example/checkout")
    resp = client.post(reverse("core:contratar_plano"), {"plano": "profissional"})
    assert resp.status_code == 302
    assert resp.headers.get("Location") == "https://pay.example/checkout"


def test_contratar_plano_sem_pagamento_configurado(client, empresa, usuario):
    resp = client.post(reverse("core:contratar_plano"), {"plano": "enterprise"})
    assert resp.status_code == 302
    assert "escolher-plano" in resp.headers.get("Location")


def test_contratar_plano_invalido_redireciona(client, usuario):
    resp = client.post(reverse("core:contratar_plano"), {"plano": "luxo"})
    assert resp.status_code == 302
    assert "escolher-plano" in resp.headers.get("Location")
