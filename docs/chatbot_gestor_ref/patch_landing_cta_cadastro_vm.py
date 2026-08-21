# -*- coding: utf-8 -*-
"""Aponta os CTAs da landing page para o cadastro self-service (30 dias de trial)."""
import os, shutil, datetime

p = "/home/ubuntu/apps/nginx-proxy/data/www/landing/index.html"
suf = datetime.date.today().strftime("%Y%m%d")
s = open(p, encoding="utf-8").read()
orig = s
URL = "https://jrsolutions.duckdns.org/cadastro/"

# 1) menu: "Começar agora"
a1 = '<a class="btn btn--accent" href="#contato">Começar agora</a>'
b1 = f'<a class="btn btn--accent" href="{URL}">Começar teste grátis</a>'
if a1 in s and URL not in s:
    assert s.count(a1) == 1, "CTA menu nao unico"
    s = s.replace(a1, b1, 1)
    print("[ok] menu -> Começar teste grátis")

# 2) hero: "Ver planos" vira o CTA de cadastro
a2 = '<a class="btn btn--accent btn--lg" href="#planos">Ver planos</a>'
b2 = f'<a class="btn btn--accent btn--lg" href="{URL}">Começar teste grátis</a>'
if a2 in s:
    assert s.count(a2) == 1, "CTA hero nao unico"
    s = s.replace(a2, b2, 1)
    print("[ok] hero -> Começar teste grátis")

if s != orig:
    bak = f"{p}.bak_cta_{suf}"
    if not os.path.exists(bak):
        shutil.copy2(p, bak)
        print(f"[backup] {p} -> {bak}")
    open(p, "w", encoding="utf-8").write(s)
    print("[ok] index.html atualizado")
else:
    print("[skip] nenhuma alteracao (ja aplicado?)")

# verifica que a URL ficou presente N vezes
print("ocorrencias da URL cadastro:", s.count(URL))
