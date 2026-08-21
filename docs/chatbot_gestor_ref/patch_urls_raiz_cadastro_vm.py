# -*- coding: utf-8 -*-
"""Adiciona alias limpo /cadastro/ na raiz (config/urls.py) da VM, com backup."""
import os, shutil, datetime, sys

p = "/home/ubuntu/Sistema_Gestor/config/urls.py"
suf = datetime.date.today().strftime("%Y%m%d")
s = open(p, encoding="utf-8").read()
orig = s

# 1) import de 'cadastro' na linha do DashboardView (com ou sem alias já aplicado)
old_imp = "from meigestao_app.core.views import DashboardView"
new_imp = "from meigestao_app.core.views import DashboardView, cadastro"
if "import DashboardView, cadastro" not in s:
    assert s.count(old_imp) == 1, "import DashboardView nao unico"
    s = s.replace(old_imp, new_imp, 1)
    print("[ok] import cadastro adicionado")

# 2) rota alias na raiz (marca unica via comentario)
if "path('cadastro/', cadastro, name='cadastro')" not in s:
    anchor = "    path('', DashboardView.as_view(), name='dashboard'),\n"
    assert s.count(anchor) == 1, "anchor dashboard raiz nao unico"
    alias = (
        anchor
        + "    # Cadastro self-service (landing): botao 'Comecar teste gratis'.\n"
        + "    path('cadastro/', cadastro, name='cadastro'),\n"
    )
    s = s.replace(anchor, alias, 1)
    print("[ok] rota /cadastro/ alias adicionada")

if s != orig:
    bak = f"{p}.bak_urls_raiz_{suf}"
    if not os.path.exists(bak):
        shutil.copy2(p, bak)
        print(f"[backup] {p} -> {bak}")
    open(p, "w", encoding="utf-8").write(s)
    print("[ok] arquivo gravado")
else:
    print("[skip] nada a alterar")

import ast
ast.parse(open(p, encoding="utf-8").read())
print("SYNTAX OK")
