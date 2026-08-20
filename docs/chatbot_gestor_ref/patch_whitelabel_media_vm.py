# -*- coding: utf-8 -*-
"""
Fix White Label -> media em producao (VM).
Serve /media/ (logo da empresa p/ white label, anexos, etc.) mesmo com DJANGO_DEBUG=False.

CAUSA-RAIZ: em Django 4.2, django.conf.urls.static.static() retorna [] quando DEBUG=False
(no-op), entao simplesmente mover o static(MEDIA_URL) para fora do `if settings.DEBUG`
NAO resolve — a rota continua ausente em producao e a URL /media/ da 404. Por isso o
white label (marca/logo do cliente) "nao funcionava".

FIX: registrar a rota media via re_path direto (django.urls.re_path + django.views.static.serve),
com imports embutidos no proprio bloco (autocontido e idempotente).

Patch minimo + backup (.bak_whitelabel_media_<ts>).
"""
import shutil, time, sys

p = "/home/ubuntu/Sistema_Gestor/config/urls.py"
s = open(p, encoding="utf-8").read()

BLOCK = """# /media/ tambem em PRODUCAO (logo da empresa p/ white label, anexos, etc.).
# ATENCAO: django.conf.urls.static.static() retorna [] quando DEBUG=False (Django 4.2),
# entao registramos via re_path direto. Fix: marca/logo do cliente nao aparecia em producao (404).
from django.urls import re_path as _re_path
from django.views.static import serve as _serve_media
urlpatterns += [
    _re_path(r"^media/(?P<path>.*)$", _serve_media,
             {"document_root": settings.MEDIA_ROOT}),
]"""

# Formas erradas que podem existir (static() nao cria rota em producao)
WRONG_FORMS = [
    "urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)",
]

if r'_re_path(r"^media/(?P<path>.*)$"' in s:
    print("ALREADY_APPLIED")
    sys.exit(0)

for wrong in WRONG_FORMS:
    if wrong in s:
        backup = p + ".bak_whitelabel_media_" + time.strftime("%Y%m%d_%H%M%S")
        shutil.copy2(p, backup)
        s = s.replace(wrong, BLOCK, 1)
        open(p, "w", encoding="utf-8").write(s)
        print("OK_BACKUP=", backup)
        print("OK_PATCHED_REPATH")
        sys.exit(0)

print("ERO: forma media/static() nao encontrada; verificar manualmente.")
for line in s.splitlines():
    if "static(" in line or "media" in line.lower() or "re_path" in line:
        print("   ", line)
sys.exit(2)
