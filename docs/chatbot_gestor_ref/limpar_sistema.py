# -*- coding: utf-8 -*-
"""LIMPA a produção: remove TODAS as empresas/dados/usuários, MANTENDO só o
superuser JRSolutionsRoque (acesso global). Faz via SQL bruto com FK off
(preserva django_migrations e o superuser; zera os demais). Não recupera dados.

Roda na VM:  sudo docker exec -e PYTHONPATH=/app -i mei_gestao_app python /dev/stdin < limpar_sistema.py
ATENÇÃO: faça backup do db.sqlite3 antes.
"""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth.models import User
from django.db import connection

SUPERUSER = "JRSolutionsRoque"

admin = User.objects.filter(username=SUPERUSER).first()
if not admin or not admin.is_superuser:
    raise SystemExit(f"ABORT: superuser {SUPERUSER} não encontrado/não é superuser.")

print("== ANTES ==")
from meigestao_app.core.models import Empresa
from meigestao_app.usuarios.models import Perfil
print("empresas:", Empresa.objects.count(), "| usuarios:", User.objects.count())

super_pk = admin.pk

# Tabelas de sistema que DEVEM ficar intactas (admin/auth/migrations)
KEEP = {"auth_group", "auth_permission", "django_content_type",
        "django_migrations", "django_admin_log", "sqlite_sequence"}

with connection.cursor() as cur:
    cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    )
    tables = [r[0] for r in cur.fetchall()]

    cur.execute("PRAGMA foreign_keys=OFF")
    for t in tables:
        if t in KEEP:
            print("  (preserva)", t)
        elif t == "auth_user":
            cur.execute("DELETE FROM auth_user WHERE id != %s", [super_pk])
            print("  (limpa, mantém superuser) auth_user")
        else:
            cur.execute(f'DELETE FROM "{t}"')  # noqa: S608 (t vem de sqlite_master)
            print("  (limpo)", t)
    # zera autoincrement das tabelas esvaziadas; mantém auth_user alinhado ao superuser
    for t in tables:
        if t in KEEP or t == "auth_user":
            continue
        cur.execute("DELETE FROM sqlite_sequence WHERE name=%s", [t])
    cur.execute(
        "UPDATE sqlite_sequence SET seq=(SELECT COALESCE(MAX(id),0) FROM auth_user) "
        "WHERE name='auth_user'"
    )
    cur.execute("PRAGMA foreign_keys=ON")

print("== DEPOIS ==")
print("empresas:", Empresa.objects.count())
print("usuarios:", User.objects.count())
print("perfis:", Perfil.objects.count())
a = User.objects.get(pk=super_pk)
print("superuser mantido:", a.username, "| staff:", a.is_staff, "| super:", a.is_superuser)
