"""Deploy do LOGIN PÚBLICO do cliente na VM de produção. Idempotente; backup
de cada arquivo em .bak_publiclogin_<ts>. Nunca sobrescreve arquivo inteiro.

Este script roda na VM a partir de um diretório de staging onde também deve
estar o arquivo `login.html` (novo template), que será copiado para a árvore.
"""
import glob
import os
import shutil
import time

BASE = "/home/ubuntu/Sistema_Gestor"
HERE = os.path.dirname(os.path.abspath(__file__))


def ts():
    return time.strftime("%Y%m%d_%H%M%S")


def backup(p: str) -> None:
    if os.path.exists(p):
        shutil.copy(p, p + f".bak_publiclogin_{ts()}")


def sub1(p, old, new, label):
    """Substitui 1 ocorrência, idempotente (se new já presente, pula)."""
    if not os.path.exists(p):
        print(f"  SKIP {p} (nao existe)"); return False
    src = open(p, encoding="utf-8").read()
    if new in src:
        return False
    if old not in src:
        print(f"  ! {label}: padrao ausente em {p}: {old[:50]!r}"); return False
    backup(p)
    open(p, "w", encoding="utf-8").write(src.replace(old, new, 1))
    print(f"  OK {label}"); return True


FUNCS = '''

@require_http_methods(["GET", "POST"])
def login_view(request):
    """Login p\\u00fablico do cliente."""
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    proximo = request.GET.get('next') or ''
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            usuario = form.get_user()
            login(request, usuario)
            messages.success(request, f'Bem-vindo(a), {usuario.first_name or usuario.username}!')
            destino = proximo or 'core:dashboard'
            if not url_has_allowed_host_and_scheme(destino, allowed_hosts={request.get_host()}):
                destino = 'core:dashboard'
            return redirect(destino)
        erros = list(form.non_field_errors()) or ['E-mail ou senha inv\\u00e1lidos.']
        return render(request, 'meigestao_app/core/login.html', {
            'form': form, 'erros': erros, 'valores': request.POST, 'next': proximo,
        })
    form = AuthenticationForm(request)
    return render(request, 'meigestao_app/core/login.html', {
        'form': form, 'erros': [], 'valores': {}, 'next': proximo,
    })


@require_http_methods(["GET", "POST"])
def logout_view(request):
    """Encerra a sess\\u00e3o e volta para o login p\\u00fablico."""
    logout(request)
    return redirect('core:login')


'''

# ---- 1) config/settings.py ------------------------------------------------
sub1(f"{BASE}/config/settings.py",
     "LOGIN_URL = 'admin:login'", "LOGIN_URL = 'core:login'", "settings.LOGIN_URL")

# ---- 2) config/urls.py: alias /entrar/ na raiz ----------------------------
U = f"{BASE}/config/urls.py"
if os.path.exists(U):
    src = open(U, encoding="utf-8").read()
    if "login_view" not in src:
        backup(U)
        if "from meigestao_app.core.views import DashboardView, cadastro" in src:
            src = src.replace(
                "from meigestao_app.core.views import DashboardView, cadastro",
                "from meigestao_app.core.views import DashboardView, cadastro, login_view", 1)
        if "path('entrar/', login_view" not in src:
            src = src.replace(
                "path('cadastro/', cadastro, name='cadastro'),\n",
                "path('cadastro/', cadastro, name='cadastro'),\n"
                "    path('entrar/', login_view, name='entrar'),\n", 1)
        open(U, "w", encoding="utf-8").write(src)
        print("  OK config/urls.py (entrar alias)")
    else:
        print("  SKIP config/urls.py (ja tem login_view)")

# ---- 3) meigestao_app/core/views.py ----------------------------------------
V = f"{BASE}/meigestao_app/core/views.py"
if os.path.exists(V):
    src = open(V, encoding="utf-8").read()
    if "def login_view(" not in src:
        backup(V)
        # imports
        src = src.replace("from django.contrib.auth import authenticate, login",
                          "from django.contrib.auth import authenticate, login, logout", 1)
        if "AuthenticationForm" not in src:
            src = src.replace(
                "from django.contrib.auth import authenticate, login, logout",
                "from django.contrib.auth import authenticate, login, logout\n"
                "from django.contrib.auth.forms import AuthenticationForm", 1)
        if "url_has_allowed_host_and_scheme" not in src:
            src = src.replace(
                "from django.contrib.auth.forms import AuthenticationForm",
                "from django.contrib.auth.forms import AuthenticationForm\n"
                "from django.utils.http import url_has_allowed_host_and_scheme", 1)
        # DashboardView
        src = src.replace("login_url = 'admin:login'", "login_url = 'core:login'", 1)
        # insere funcoes antes do primeiro 'class '
        anchor = "class HomeView(" if "class HomeView(" in src else "class DashboardView("
        if anchor in src:
            src = src.replace(anchor, FUNCS.lstrip("\n") + anchor, 1)
        open(V, "w", encoding="utf-8").write(src)
        print("  OK core/views.py (login/logout + imports)")
    else:
        print("  SKIP core/views.py (login_view ja existe)")

# ---- 4) meigestao_app/core/urls.py: entrar/sair ----------------------------
sub1(f"{BASE}/meigestao_app/core/urls.py",
     "    path('bot/contexto/', views.bot_contexto, name='bot_contexto'),",
     "    path('entrar/', views.login_view, name='login'),\n"
     "    path('sair/', views.logout_view, name='logout'),\n"
     "    path('bot/contexto/', views.bot_contexto, name='bot_contexto'),",
     "core/urls.py entrar/sair")

# ---- 5) login_url admin -> core em todas as views ---------------------------
total = 0
for p in glob.glob(f"{BASE}/meigestao_app/**/views.py", recursive=True):
    if "migrations" in p:
        continue
    s = open(p, encoding="utf-8").read()
    n = s.count("login_url = 'admin:login'")
    if n:
        backup(p)
        open(p, "w", encoding="utf-8").write(
            s.replace("login_url = 'admin:login'", "login_url = 'core:login'"))
        total += n
print(f"  login_url admin->core: {total} ocorrencia(s)")

# ---- 6) templates -----------------------------------------------------------
tmpl = os.path.join(HERE, "login.html")
dst = f"{BASE}/templates/meigestao_app/core/login.html"
if os.path.exists(tmpl):
    shutil.copy(tmpl, dst)
    print("  OK login.html copiado")
else:
    print(f"  ! login.html nao encontrado em {tmpl} (copie junto no staging)")

sub1(f"{BASE}/templates/meigestao_app/core/cadastro.html",
     'href="/admin/login/"', "href=\"{% url 'core:login' %}\"",
     "cadastro.html footer")
sub1(f"{BASE}/templates/base.html",
     '<a class="dropdown-item text-danger" href="/admin/logout/"',
     "<a class=\"dropdown-item text-danger\" href=\"{% url 'core:logout' %}\"",
     "base.html logout")
sub1(f"{BASE}/templates/includes/navbar.html",
     "{% url 'admin:logout' %}", "{% url 'core:logout' %}",
     "navbar.html logout")
for p in [f"{BASE}/templates/meigestao_app/almoxarifado/base_almoxarifado.html"]:
    if os.path.exists(p):
        s = open(p, encoding="utf-8").read()
        if 'href="/admin/logout/"' in s:
            backup(p)
            open(p, "w", encoding="utf-8").write(
                s.replace('href="/admin/logout/"', 'href="{% url \'core:logout\' %}"'))
            print("  OK almoxarifado logout")
        else:
            print("  SKIP almoxarifado (ja ok/ausente)")

print("\nFIM. Depois rode:")
print("  sudo docker exec mei_gestao_app python manage.py check")
print("  sudo docker restart mei_gestao_app")
