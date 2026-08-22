"""Deploy das Páginas Legais (LGPD: Privacidade + Termos) na VM de produção.
Idempotente; backup de cada arquivo em .bak_lgpd_<ts>. Nunca sobrescreve arquivo
inteiro. Roda na VM a partir de um staging onde também estão os templates novos
(legal_base.html, privacidade.html, termos.html).
"""
import os
import shutil
import time

BASE = "/home/ubuntu/Sistema_Gestor"
HERE = os.path.dirname(os.path.abspath(__file__))


def ts():
    return time.strftime("%Y%m%d_%H%M%S")


def backup(p: str) -> None:
    if os.path.exists(p):
        shutil.copy(p, p + f".bak_lgpd_{ts()}")


def sub1(p, old, new, label):
    if not os.path.exists(p):
        print(f"  SKIP {p} (nao existe)"); return False
    src = open(p, encoding="utf-8").read()
    if new in src:
        print(f"  SKIP {label} (ja aplicado)"); return True
    if old not in src:
        print(f"  ! {label}: padrao ausente em {p}: {old[:50]!r}"); return False
    backup(p)
    open(p, "w", encoding="utf-8").write(src.replace(old, new, 1))
    print(f"  OK {label}"); return True


FUNCS = '''

def privacidade(request):
    """P\\u00e1gina p\\u00fablica de Pol\\u00edtica de Privacidade (LGPD)."""
    return render(request, 'meigestao_app/core/privacidade.html')


def termos(request):
    """P\\u00e1gina p\\u00fablica de Termos de Uso."""
    return render(request, 'meigestao_app/core/termos.html')


'''

# 1) core/views.py: adiciona privacidade/termos antes de class HomeView
V = f"{BASE}/meigestao_app/core/views.py"
if os.path.exists(V):
    src = open(V, encoding="utf-8").read()
    if "def privacidade(" not in src:
        backup(V)
        anchor = "class HomeView(" if "class HomeView(" in src else "class DashboardView("
        src = src.replace(anchor, FUNCS.lstrip("\n") + anchor, 1)
        open(V, "w", encoding="utf-8").write(src)
        print("  OK core/views.py (privacidade/termos)")
    else:
        print("  SKIP core/views.py (privacidade ja existe)")

# 2) core/urls.py: rotas antes do bot/contexto
CU2 = f"{BASE}/meigestao_app/core/urls.py"
if os.path.exists(CU2):
    src = open(CU2, encoding="utf-8").read()
    if "path('privacidade/'" not in src:
        backup(CU2)
        src = src.replace(
            "    path('bot/contexto/', views.bot_contexto, name='bot_contexto'),",
            "    # Páginas públicas legais (LGPD / termos).\n"
            "    path('privacidade/', views.privacidade, name='privacidade'),\n"
            "    path('termos/', views.termos, name='termos'),\n"
            "    path('bot/contexto/', views.bot_contexto, name='bot_contexto'),", 1)
        open(CU2, "w", encoding="utf-8").write(src)
        print("  OK core/urls.py (privacidade/termos)")
    else:
        print("  SKIP core/urls.py (ja tem)")

# 3) config/urls.py: import + aliases /privacidade/ /termos/
CU = f"{BASE}/config/urls.py"
if os.path.exists(CU):
    src = open(CU, encoding="utf-8").read()
    changed = False
    if "privacidade, termos" not in src:
        backup(CU)
        if "login_view" in src:
            src = src.replace(
                "login_view,", "login_view,\n                                      privacidade, termos", 1)
        else:
            src = src.replace(
                "from meigestao_app.core.views import DashboardView, cadastro",
                "from meigestao_app.core.views import (DashboardView, cadastro,\n"
                "                                      privacidade, termos)", 1)
        if "path('privacidade/'" not in src:
            src = src.replace(
                "path('entrar/', login_view, name='entrar'),",
                "path('entrar/', login_view, name='entrar'),\n"
                "    path('privacidade/', privacidade, name='privacidade'),\n"
                "    path('termos/', termos, name='termos'),", 1)
        open(CU, "w", encoding="utf-8").write(src)
        changed = True
        print("  OK config/urls.py (privacidade/termos aliases)")
    else:
        print("  SKIP config/urls.py (ja tem)")

# 4) templates novos
for t in ["legal_base.html", "privacidade.html", "termos.html"]:
    s = os.path.join(HERE, t)
    d = f"{BASE}/templates/meigestao_app/core/{t}"
    if os.path.exists(s):
        shutil.copy(s, d); print(f"  OK template {t}")
    else:
        print(f"  ! template {t} nao esta no staging: {s}")

# 5) login.html footer: links legais
sub1(f"{BASE}/templates/meigestao_app/core/login.html",
     "Não tem uma conta? <a href=\"{% url 'core:cadastro' %}\">Criar conta grátis</a> — 30 dias grátis.",
     "Não tem uma conta? <a href=\"{% url 'core:cadastro' %}\">Criar conta grátis</a> — 30 dias grátis.<br>\n"
     "        <a href=\"{% url 'core:termos' %}\">Termos de Uso</a> &middot; "
     "<a href=\"{% url 'core:privacidade' %}\">Privacidade (LGPD)</a>",
     "login.html footer legal")

# 6) cadastro.html: termos/privacidade como links
sub1(f"{BASE}/templates/meigestao_app/core/cadastro.html",
     "você concorda com os termos de uso.",
     "você concorda com os <a href=\"{% url 'core:termos' %}\" style=\"color:inherit\">termos de uso</a> e com a <a href=\"{% url 'core:privacidade' %}\" style=\"color:inherit\">política de privacidade (LGPD)</a>.",
     "cadastro.html termos/privacidade")

print("\nFIM. Depois rode: sudo docker exec mei_gestao_app python manage.py check")
