# -*- coding: utf-8 -*-
"""CA2 — O app on-premise usa o Postgres que o compose provisiona.

Contexto (spec docs/SPECS/pacote-on-premise-v25.md, defeito D3):

O `config/settings.py` fazia:

    if env('DB_TYPE') == 'postgres':
        DATABASES = {'default': env.db()}

Mas `env.db()` do django-environ só lê a variável **DATABASE_URL**
(`postgres://user:pass@host:port/db`). O `.env` do pacote on-premise
fornece `DB_NAME`/`DB_USER`/`DB_PASSWORD`/`DB_HOST`/`DB_PORT` (o formato
que o compose usa via `POSTGRES_DB`/`POSTGRES_USER`/...).

Resultado: com `DB_TYPE=postgres` e sem `DATABASE_URL`, o Django morre com
`ImproperlyConfigured: Set the DATABASE_URL environment variable` — ou,
pior, cai no default do env.db() e aponta para outro banco.

Este teste carrega o settings de verdade, em subprocesso (o settings é
módulo-level e tem efeitos colaterais), e confere que o ENGINE e os
parâmetros saem das variáveis `DB_*`.
"""
import os
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[2]


# ── CA2 ────────────────────────────────────────────────────────────────

CA2_ENV = {
    "DJANGO_SECRET_KEY": "audit-temp-key-not-production-1234567890",
    "DJANGO_DEBUG": "False",
    "DJANGO_ALLOWED_HOSTS": "localhost",
    "DB_TYPE": "postgres",
    "DB_NAME": "gestor",
    "DB_USER": "gestor",
    "DB_PASSWORD": "senha-de-teste",
    "DB_HOST": "db",
    "DB_PORT": "5432",
}

CA2_SCRIPT = """
import os, json
os.environ.update(json.loads(os.environ["CA2_ENV_JSON"]))
# Garante que DATABASE_URL NÃO existe (o pacote não a usa)
os.environ.pop("DATABASE_URL", None)

import django
django.setup()

from django.conf import settings
db = settings.DATABASES["default"]
print(json.dumps({
    "ENGINE": db.get("ENGINE"),
    "NAME": str(db.get("NAME")),
    "HOST": db.get("HOST"),
    "PORT": str(db.get("PORT")),
    "USER": db.get("USER"),
}))
"""


def _carregar_settings(env_extra: dict) -> dict:
    env = dict(os.environ)
    env.update(env_extra)
    env["CA2_ENV_JSON"] = __import__("json").dumps(env_extra)
    proc = subprocess.run(
        [sys.executable, "-c", CA2_SCRIPT],
        cwd=str(RAIZ),
        env=env,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, (
        "o settings.py não subiu com as variáveis do pacote on-premise:\n"
        f"stdout: {proc.stdout}\nstderr: {proc.stderr}"
    )
    return __import__("json").loads(proc.stdout.strip().splitlines()[-1])


def test_ca2_db_postgres_vem_das_variaveis_db():
    """CA2: com DB_TYPE=postgres e as variáveis DB_*, o ENGINE precisa ser
    postgresql e NAME/HOST/PORT/USER precisam vir das próprias variáveis —
    sem depender de DATABASE_URL."""
    db = _carregar_settings(CA2_ENV)

    assert db["ENGINE"] == "django.db.backends.postgresql", (
        f"com DB_TYPE=postgres o ENGINE deveria ser postgresql, achou {db['ENGINE']!r}"
    )
    assert db["NAME"] == "gestor", f"NAME deveria vir de DB_NAME, achou {db['NAME']!r}"
    assert db["HOST"] == "db", f"HOST deveria vir de DB_HOST, achou {db['HOST']!r}"
    assert db["PORT"] == "5432", f"PORT deveria vir de DB_PORT, achou {db['PORT']!r}"
    assert db["USER"] == "gestor", f"USER deveria vir de DB_USER, achou {db['USER']!r}"


def test_ca2_settings_nao_exige_database_url():
    """CA2 (complemento): o pacote on-premise NÃO pede DATABASE_URL.

    Se o settings exigir DATABASE_URL, o cliente precisa montar uma URL
    à mão — e o `instalar.sh` não faz isso. O `.env.example` do pacote
    traz `DB_*`, e é com elas que o app tem de funcionar.
    """
    texto = (RAIZ / "config" / "settings.py").read_text(encoding="utf-8")
    # Ignora comentários — só conta uso real em código.
    linhas_codigo = [
        l for l in texto.splitlines()
        if l.strip() and not l.strip().startswith("#")
    ]
    assert "env.db()" not in "\n".join(linhas_codigo), (
        "config/settings.py ainda usa env.db() em código — ele só lê "
        "DATABASE_URL, que o .env do pacote on-premise não define"
    )


def test_ca2_sqlite_continua_funcionando():
    """CA2 (não-quebra): a nuvem usa DB_TYPE=sqlite e não pode mudar."""
    env = dict(CA2_ENV)
    env["DB_TYPE"] = "sqlite"
    db = _carregar_settings(env)
    assert db["ENGINE"] == "django.db.backends.sqlite3", (
        f"DB_TYPE=sqlite deveria manter o engine sqlite, achou {db['ENGINE']!r}"
    )
