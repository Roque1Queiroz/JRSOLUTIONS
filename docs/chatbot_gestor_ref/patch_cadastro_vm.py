# -*- coding: utf-8 -*-
"""Cadastro self-service na VM (30 dias de trial + Empresa + usuário admin).

Aplica em /home/ubuntu/Sistema_Gestor:
  1) views.py  -> imports (User/Perfil/authenticate/login) + view 'cadastro'
  2) urls.py   -> rota /cadastro/
  3) cria templates/meigestao_app/core/cadastro.html

Idempotente (pode rodar de novo). Faz backup .bak_cadastro_<data> antes de editar.
Uso:  python3 patch_cadastro_vm.py
"""
import os
import shutil
import datetime

BASE = "/home/ubuntu/Sistema_Gestor"
VIEWS = os.path.join(BASE, "meigestao_app/core/views.py")
URLS = os.path.join(BASE, "meigestao_app/core/urls.py")
TPL = os.path.join(BASE, "templates/meigestao_app/core/cadastro.html")
SUF = datetime.date.today().strftime("%Y%m%d")


def backup(path):
    if os.path.exists(path):
        bak = f"{path}.bak_cadastro_{SUF}"
        if not os.path.exists(bak):
            shutil.copy2(path, bak)
            print(f"[backup] {path} -> {bak}")
        else:
            print(f"[backup] ja existe: {bak}")


TEMPLATE_HTML = """{% load static %}<!DOCTYPE html>
<html lang="pt-br">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Criar conta grátis — SISTEMA GESTOR</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css" rel="stylesheet">
<style>
    :root{--pg:linear-gradient(135deg,#4f46e5 0%,#7c3aed 100%)}
    *{font-family:'Inter',system-ui,sans-serif}
    body{margin:0;min-height:100vh;background:#f8fafc;display:flex;align-items:center;justify-content:center;padding:24px}
    .wrap{width:100%;max-width:500px}
    .brand{text-align:center;margin-bottom:22px;color:#1e293b}
    .brand .logo{font-size:1.7rem;font-weight:800;letter-spacing:.5px;background:var(--pg);-webkit-background-clip:text;background-clip:text;color:transparent}
    .brand p{color:#64748b;font-size:.9rem;margin:.2rem 0 0}
    .card{border:1px solid #e2e8f0;border-radius:18px;box-shadow:0 15px 40px -12px rgba(30,41,59,.18);padding:30px}
    .card h1{font-size:1.35rem;font-weight:700;color:#1e293b;margin-bottom:4px}
    .card .sub{color:#64748b;font-size:.88rem;margin-bottom:22px}
    .trial-badge{display:inline-flex;align-items:center;gap:6px;background:#ecfdf3;color:#067647;border:1px solid #abe3c7;font-size:.78rem;font-weight:600;padding:5px 11px;border-radius:999px;margin-top:10px}
    .form-label{font-size:.82rem;font-weight:600;color:#334155}
    .form-control,.form-select{border-radius:10px;padding:.55rem .8rem;border-color:#e2e8f0;font-size:.92rem}
    .form-control:focus,.form-select:focus{border-color:#7c3aed;box-shadow:0 0 0 .2rem rgba(124,58,237,.12)}
    .row-gap>*{margin-bottom:.9rem}
    .btn-primary{background:var(--pg);border:none;border-radius:10px;padding:.7rem;font-weight:700;font-size:.95rem}
    .btn-primary:hover{opacity:.92}
    .alert-danger{border-radius:10px;font-size:.85rem;padding:.6rem .9rem}
    .foot{text-align:center;margin-top:16px;color:#64748b;font-size:.85rem}
    .foot a{color:#4f46e5;font-weight:600;text-decoration:none}
    .disabled-hint{font-size:.72rem;color:#94a3b8;margin-top:8px}
</style>
</head>
<body>
<div class="wrap">
    <div class="brand">
        <div class="logo">⚙ SISTEMA GESTOR</div>
        <p>Gestão completa para o seu negócio</p>
    </div>

    <div class="card">
        <h1>Criar conta grátis</h1>
        <p class="sub">Preencha os dados abaixo. Sua empresa já nasce com <strong>30 dias de teste grátis</strong> e acesso total.</p>

        <div class="trial-badge"><i class="bi bi-stars"></i> 30 dias grátis &middot; sem cartão &middot; acesso total</div>

        {% if erros %}
        <div class="alert alert-danger mt-3 mb-0">
            <ul class="mb-0 ps-3">
                {% for e in erros %}<li>{{ e }}</li>{% endfor %}
            </ul>
        </div>
        {% endif %}

        <form method="post" action="{% url 'core:cadastro' %}" class="mt-3" novalidate>
            {% csrf_token %}
            <div class="row-gap">
                <div class="form-group">
                    <label class="form-label" for="nome_empresa">Nome da empresa</label>
                    <input class="form-control" id="nome_empresa" name="nome_empresa" required
                           value="{{ valores.nome_empresa }}" placeholder="Ex.: Loja do João ME">
                </div>
                <div class="form-group">
                    <label class="form-label" for="cnpj">CNPJ</label>
                    <input class="form-control" id="cnpj" name="cnpj" required
                           value="{{ valores.cnpj }}" placeholder="00.000.000/0001-00">
                </div>
                <div class="row">
                    <div class="col-6">
                        <div class="form-group">
                            <label class="form-label" for="primeiro_nome">Seu nome</label>
                            <input class="form-control" id="primeiro_nome" name="primeiro_nome" required
                                   value="{{ valores.primeiro_nome }}" placeholder="Nome">
                        </div>
                    </div>
                    <div class="col-6">
                        <div class="form-group">
                            <label class="form-label" for="sobrenome">Sobrenome</label>
                            <input class="form-control" id="sobrenome" name="sobrenome"
                                   value="{{ valores.sobrenome }}" placeholder="Sobrenome">
                        </div>
                    </div>
                </div>
                <div class="form-group">
                    <label class="form-label" for="email">E-mail (login)</label>
                    <input type="email" class="form-control" id="email" name="email" required autocomplete="email"
                           value="{{ valores.email }}" placeholder="voce@empresa.com.br">
                </div>
                <div class="row">
                    <div class="col-6">
                        <div class="form-group">
                            <label class="form-label" for="senha">Senha</label>
                            <input type="password" class="form-control" id="senha" name="senha" required
                                   minlength="8" autocomplete="new-password" placeholder="Mín. 8 caracteres">
                        </div>
                    </div>
                    <div class="col-6">
                        <div class="form-group">
                            <label class="form-label" for="confirma">Confirmar senha</label>
                            <input type="password" class="form-control" id="confirma" name="confirma" required
                                   minlength="8" autocomplete="new-password" placeholder="Repita a senha">
                        </div>
                    </div>
                </div>
                <button type="submit" class="btn btn-primary w-100">
                    Criar conta e começar <i class="bi bi-arrow-right ms-1"></i>
                </button>
                <p class="disabled-hint">Ao criar a conta você concorda com os termos de uso. Os 30 dias dão acesso a todos os módulos; ao final, basta escolher um plano para continuar.</p>
            </div>
        </form>
    </div>

    <div class="foot">Já tem uma conta? <a href="/admin/login/">Entrar</a></div>
</div>
</body>
</html>
"""


def aplicar(path, antiga, nova, guarda_ja_tem):
    s = open(path, encoding="utf-8").read()
    if guarda_ja_tem in s:
        print(f"[skip] {path}: ja contem '{guarda_ja_tem}'")
        return
    assert s.count(antiga) == 1, f"anchor nao unica em {path}: {antiga!r}"
    backup(path)
    s = s.replace(antiga, nova, 1)
    open(path, "w", encoding="utf-8").write(s)
    print(f"[ok] patch em {path}")


# ── 1) views.py ─────────────────────────────────────────────
anchor_imp = (
    "from django.contrib.auth.decorators import login_required\n"
    "from django.views.generic import TemplateView, CreateView, UpdateView, DeleteView, ListView"
)
novo_imp = (
    "from django.contrib.auth.decorators import login_required\n"
    "from django.contrib.auth import authenticate, login\n"
    "from django.contrib.auth.models import User\n"
    "from django.views.decorators.http import require_http_methods\n"
    "from meigestao_app.usuarios.models import Perfil\n"
    "import datetime\n"
    "from django.views.generic import TemplateView, CreateView, UpdateView, DeleteView, ListView"
)
aplicar(VIEWS, anchor_imp, novo_imp, "require_http_methods")

ANCORA_VIS = "class HomeView(TemplateView):"
if not open(VIEWS, encoding="utf-8").read().count("def cadastro("):
    CADASTRO = '''@require_http_methods(["GET", "POST"])
def cadastro(request):
    """Cadastro self-service: o visitante cria a conta na própria landing page e já
    ganha os 30 dias de teste grátis (Empresa nasce como Enterprise em teste, acesso
    total). O primeiro usuário é o administrador (admin) da empresa, e já sai logado.
    """
    if request.user.is_authenticated:
        return redirect('core:dashboard')

    erros = []
    if request.method == 'POST':
        nome = (request.POST.get('nome_empresa') or '').strip()
        cnpj = (request.POST.get('cnpj') or '').strip()
        primeiro_nome = (request.POST.get('primeiro_nome') or '').strip()
        sobrenome = (request.POST.get('sobrenome') or '').strip()
        email = (request.POST.get('email') or '').strip().lower()
        senha = request.POST.get('senha') or ''
        confirma = request.POST.get('confirma') or ''

        if not nome:
            erros.append('Informe o nome da empresa.')
        if not cnpj:
            erros.append('Informe o CNPJ da empresa.')
        if not primeiro_nome:
            erros.append('Informe seu primeiro nome.')
        if not email or '@' not in email:
            erros.append('Informe um e-mail válido.')
        if len(senha) < 8:
            erros.append('A senha deve ter pelo menos 8 caracteres.')
        if senha and senha != confirma:
            erros.append('A confirmação de senha não confere.')

        if not erros:
            if Empresa.objects.filter(cnpj=cnpj).exists():
                erros.append('Já existe uma conta com este CNPJ. Se for sua, faça login.')
            elif Empresa.objects.filter(nome__iexact=nome).exists():
                erros.append('Já existe uma empresa com este nome.')
            if User.objects.filter(username=email).exists():
                erros.append('Já existe uma conta com este e-mail.')

        if not erros:
            # Cria a empresa e já inicia os 30 dias de teste (acesso total).
            empresa = Empresa.objects.create(nome=nome, cnpj=cnpj, email=email, ativa=True)
            empresa.iniciar_teste()

            usuario = User.objects.create_user(
                username=email, email=email, password=senha,
                first_name=primeiro_nome, last_name=sobrenome,
            )
            Perfil.objects.create(
                usuario=usuario, empresa=empresa, permissao='admin',
                data_admissao=datetime.date.today(), ativo=True,
            )

            # Auto-login: o visitante cai direto no dashboard já usando.
            autenticado = authenticate(username=email, password=senha)
            if autenticado is not None:
                login(request, autenticado)
            messages.success(
                request,
                f'Bem-vindo(a)! Sua conta foi criada com 30 dias de teste grátis '
                f'(até {empresa.trial_expira_em:%d/%m/%Y}).',
            )
            return redirect('core:dashboard')

    return render(request, 'meigestao_app/core/cadastro.html', {
        'erros': erros,
        'valores': request.POST if request.method == 'POST' else {},
    })


'''
    s = open(VIEWS, encoding="utf-8").read()
    assert s.count(ANCORA_VIS) == 1, "HomeView nao unico"
    backup(VIEWS)
    s = s.replace(ANCORA_VIS, CADASTRO + ANCORA_VIS, 1)
    open(VIEWS, "w", encoding="utf-8").write(s)
    print("[ok] view cadastro inserida em views.py")
else:
    print("[skip] views.py ja tem def cadastro")

# ── 2) urls.py ──────────────────────────────────────────────
anchor_url = (
    "    path('asaas/webhook/', views.asaas_webhook, name='asaas_webhook'),\n"
    "    # Endpoint JSON seguro que alimenta o assistente de IA com dados da empresa."
)
nova_url = (
    "    path('asaas/webhook/', views.asaas_webhook, name='asaas_webhook'),\n"
    "    # Cadastro self-service (landing): cria Empresa + usuário admin + 30 dias de trial.\n"
    "    path('cadastro/', views.cadastro, name='cadastro'),\n"
    "    # Endpoint JSON seguro que alimenta o assistente de IA com dados da empresa."
)
aplicar(URLS, anchor_url, nova_url, "path('cadastro/'")

# ── 3) template ─────────────────────────────────────────────
os.makedirs(os.path.dirname(TPL), exist_ok=True)
if os.path.exists(TPL):
    print(f"[skip] template ja existe: {TPL}")
else:
    TPL_CONTENT = TEMPLATE_HTML
    open(TPL, "w", encoding="utf-8").write(TPL_CONTENT)
    print(f"[ok] template criado: {TPL}")

print("FIM")

