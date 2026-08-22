# -*- coding: utf-8 -*-
"""Valida acao dos usuarios de teste (vendedor x operador) na VM."""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse


def testa(username, rotas):
    c = Client(SERVER_NAME="jrsolutions.duckdns.org")
    u = User.objects.get(username=username)
    c.force_login(u)
    print("=== %s (%s) ===" % (username.upper(), u.perfil.permissao))
    for n, url in rotas:
        try:
            r = c.get(url, secure=True)
            print("   %-32s -> %s" % (n, r.status_code))
        except Exception as e:
            print("   %-32s -> EXC %s" % (n, type(e).__name__))


ROTAS = [
    ("visao geral", "/"),
    ("clientes list", reverse("clientes:cliente_list")),
    ("clientes criar", reverse("clientes:cliente_create")),
    ("vendas list", reverse("vendas:venda_list")),
    ("vendas criar", reverse("vendas:venda_create")),
    ("estoque produtos", reverse("estoque:produto_list")),
    ("financeiro caixa", reverse("financeiro:transacao_lista")),
    ("financeiro criar", reverse("financeiro:transacao_criar")),
]

if __name__ == "__main__":
    import sys
    who = sys.argv[1] if len(sys.argv) > 1 else "operador_teste"
    testa(who, ROTAS)
