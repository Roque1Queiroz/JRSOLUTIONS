# -*- coding: utf-8 -*-
"""Testes do teste grátis (30 dias de acesso total) + bloqueio após o término."""
import datetime

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

from meigestao_app.core.models import Empresa
from meigestao_app.usuarios.models import Perfil


@pytest.fixture
def empresa_trial(db):
    e = Empresa.objects.create(nome="Cliente Trial", cnpj="88.888.888/0001-88")
    e.iniciar_teste(dias=30)
    e.refresh_from_db()
    return e


@pytest.fixture
def usuario_trial(db, empresa_trial):
    u = User.objects.create_user(username="trial_user", password="senha-forte")
    Perfil.objects.create(
        usuario=u, empresa=empresa_trial, permissao="admin",
        data_admissao=datetime.date.today(),
    )
    return u


def _usuario_de(empresa, username="u"):
    u = User.objects.create_user(username=username, password="senha-forte")
    Perfil.objects.create(
        usuario=u, empresa=empresa, permissao="admin",
        data_admissao=datetime.date.today(),
    )
    return u


def test_iniciar_teste_define_enterprise_e_data_futura(db):
    e = Empresa.objects.create(nome="A", cnpj="81.111.111/0001-81")
    e.iniciar_teste(dias=30)
    e.refresh_from_db()
    assert e.plano == "enterprise"
    assert e.trial_expira_em is not None
    assert e.trial_expira_em > timezone.now()
    assert e.em_teste is True
    assert e.teste_expirado is False


def test_em_teste_dentro_da_janela(db, empresa_trial):
    assert empresa_trial.em_teste is True
    assert empresa_trial.teste_expirado is False
    assert empresa_trial.plano == "enterprise"


def test_teste_expirado_apos_data(db):
    e = Empresa.objects.create(nome="B", cnpj="82.222.222/0001-82")
    e.iniciar_teste(dias=30)
    e.trial_expira_em = timezone.now() - datetime.timedelta(days=1)
    e.save(update_fields=["trial_expira_em"])
    e.refresh_from_db()
    assert e.teste_expirado is True
    assert e.em_teste is False


def test_converter_plano_limpa_trial(db, empresa_trial):
    empresa_trial.converter_plano("profissional")
    empresa_trial.refresh_from_db()
    assert empresa_trial.plano == "profissional"
    assert empresa_trial.trial_expira_em is None
    assert empresa_trial.em_teste is False
    assert empresa_trial.teste_expirado is False


def test_middleware_bloqueia_teste_expirado_para_dashboard(client, db):
    e = Empresa.objects.create(nome="C", cnpj="83.333.333/0001-83")
    e.iniciar_teste(dias=30)
    e.trial_expira_em = timezone.now() - datetime.timedelta(days=1)
    e.save(update_fields=["trial_expira_em"])
    e.refresh_from_db()
    u = _usuario_de(e, "expirado")
    client.force_login(u)
    resp = client.get(reverse("core:dashboard"))
    assert resp.status_code in (302, 403)
    assert "escolher-plano" in (resp.headers.get("Location") or "")


def test_middleware_libera_teste_ativo(client, db, empresa_trial, usuario_trial):
    client.force_login(usuario_trial)
    resp = client.get(reverse("core:dashboard"))
    assert resp.status_code == 200


def test_escolher_plano_render(client, db, usuario_trial):
    client.force_login(usuario_trial)
    resp = client.get(reverse("core:escolher_plano"))
    assert resp.status_code == 200
    assert "Básico" in resp.content.decode()
    assert "Profissional" in resp.content.decode()
    assert "Enterprise" in resp.content.decode()


def test_superuser_nao_bloqueado(client, db):
    e = Empresa.objects.create(nome="D", cnpj="84.444.444/0001-84")
    e.iniciar_teste(dias=30)
    e.trial_expira_em = timezone.now() - datetime.timedelta(days=1)
    e.save(update_fields=["trial_expira_em"])
    sup = User.objects.create_superuser(username="root", password="senha-forte")
    client.force_login(sup)
    resp = client.get(reverse("core:dashboard"))
    assert resp.status_code == 200
