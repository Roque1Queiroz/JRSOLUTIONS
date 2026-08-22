"""Deploy do Painel Executivo em Modo Demonstração (/demo/) na VM.
Idempotente; backup dos arquivos python alterados. Copia os módulos novos
deste diretório (staging) para a árvore do app e injeta as rotas/import.
"""
import os
import shutil
import time

BASE = "/home/ubuntu/Sistema_Gestor"
HERE = os.path.dirname(os.path.abspath(__file__))


def ts(): return time.strftime("%Y%m%d_%H%M%S")


def backup(p):
    if os.path.exists(p):
        shutil.copy(p, p + f".bak_demo_{ts()}")


def copy_new(rel):
    s = os.path.join(HERE, rel)
    d = os.path.join(BASE, rel)
    if os.path.exists(s):
        os.makedirs(os.path.dirname(d), exist_ok=True)
        shutil.copy(s, d)
        print("  OK copie:", rel)
    else:
        print(f"  ! falta no staging: {rel}")


def sub1(p, old, new, label):
    if not os.path.exists(p): print(f"  SKIP {p}"); return
    src = open(p, encoding="utf-8").read()
    if new in src:
        print(f"  SKIP {label} (ja aplicado)"); return
    if old not in src:
        print(f"  ! {label}: padrao ausente em {p}: {old[:50]!r}"); return
    backup(p)
    open(p, "w", encoding="utf-8").write(src.replace(old, new, 1))
    print(f"  OK {label}")


# 1) novos arquivos/módulos
for rel in ["meigestao_app/core/demo_data.py",
            "meigestao_app/core/demo_views.py",
            "meigestao_app/core/management/__init__.py",
            "meigestao_app/core/management/commands/__init__.py",
            "meigestao_app/core/management/commands/seed_demo.py",
            "templates/meigestao_app/core/demo_dashboard.html"]:
    copy_new(rel)

# 2) views.py: import do demo_views
sub1(f"{BASE}/meigestao_app/core/views.py",
     "from . import asaas\n",
     "from . import asaas\nfrom .demo_views import demo_dashboard\n",
     "views.py import demo_views")

# 3) config/urls.py: import + rota /demo/
CU = f"{BASE}/config/urls.py"
if os.path.exists(CU):
    src = open(CU, encoding="utf-8").read()
    changed = False
    if "demo_dashboard" not in src:
        backup(CU)
        src = src.replace("privacidade, termos)", "privacidade, termos, demo_dashboard)", 1)
        src = src.replace(
            "    path('termos/', termos, name='termos'),",
            "    path('termos/', termos, name='termos'),\n"
            "    # Painel executivo em modo DEMONSTRAÇÃO (público, para vender).\n"
            "    path('demo/', demo_dashboard, name='demo'),", 1)
        open(CU, "w", encoding="utf-8").write(src)
        changed = True
        print("  OK config/urls.py (demo)")
    else:
        print("  SKIP config/urls.py (ja tem demo)")

print("\nFIM. Depois rode:")
print("  sudo docker exec mei_gestao_app python manage.py check")
print("  sudo docker exec mei_gestao_app python manage.py seed_demo")
print("  sudo docker restart mei_gestao_app")
