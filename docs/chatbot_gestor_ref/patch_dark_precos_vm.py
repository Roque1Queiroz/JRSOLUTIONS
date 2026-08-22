# -*- coding: utf-8 -*-
"""Corrige visibilidade dos precos no modo escuro (base.html da VM).
Adiciona regras [data-bs-theme=dark] para .text-dark (cinza-claro), .text-muted e .bg-light."""
p = "/home/ubuntu/Sistema_Gestor/templates/base.html"
s = open(p, encoding="utf-8").read()

anchor = "            --text-primary: #f1f5f9;\n            --text-secondary: #94a3b8;\n        }"
ins = (
    "            --text-primary: #f1f5f9;\n"
    "            --text-secondary: #94a3b8;\n"
    "        }\n"
    "\n"
    "        /* Dark mode: textos fixos (precos de cards, destaques) ficam legiveis */\n"
    "        [data-bs-theme=\"dark\"] .text-dark {\n"
    "            color: #d4d4d8 !important;   /* cinza-claro legivel sobre superficie escura */\n"
    "        }\n"
    "        [data-bs-theme=\"dark\"] .text-muted {\n"
    "            color: var(--color-text-secondary) !important;\n"
    "        }\n"
    "        [data-bs-theme=\"dark\"] .bg-light {\n"
    "            background-color: var(--color-surface-raised) !important;\n"
    "        }"
)

if "[data-bs-theme=\"dark\"] .text-dark" in s:
    print("SKIP: regra dark ja presente")
else:
    assert anchor in s, "anchor nao encontrada"
    assert s.count(anchor) == 1, "anchor nao unica"
    s = s.replace(anchor, ins, 1)
    open(p, "w", encoding="utf-8").write(s)
    print("OK: regras dark inseridas no base.html da VM")
