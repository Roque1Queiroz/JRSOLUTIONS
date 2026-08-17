# -*- coding: utf-8 -*-
"""Adiciona a rota bot/contexto no urls.py da VM (idempotente)."""
p = "/home/ubuntu/Sistema_Gestor/meigestao_app/core/urls.py"
s = open(p, encoding="utf-8").read()

if "bot/contexto" in s:
    print("OK: rota bot/contexto ja presente, nada a fazer")
    raise SystemExit(0)

if "path('plano/', views.plano_detail, name='plano_detail')," in s:
    old = "path('plano/', views.plano_detail, name='plano_detail'),"
    new = ("path('plano/', views.plano_detail, name='plano_detail'),\n"
           "    # Endpoint JSON seguro que alimenta o assistente de IA com dados da empresa.\n"
           "    path('bot/contexto/', views.bot_contexto, name='bot_contexto'),")
    s = s.replace(old, new, 1)
else:
    # fallback: insere antes do fechamento da lista
    assert s.rstrip().endswith("]"), "urlpatterns nao termina em ]"
    ins = ("    path('bot/contexto/', views.bot_contexto, name='bot_contexto'),\n"
           "]\n")
    s = s.rstrip()
    s = s[:-1] + ins  # remove o ] final e recoloca com a rota nova
open(p, "w", encoding="utf-8").write(s)
print("OK: rota bot/contexto adicionada no urls.py da VM")
