# -*- coding: utf-8 -*-
"""Cria usuarios reais da equipe na empresa JR Solutions Tecnologia.

Uso (na VM, dentro do container):
    docker exec -i mei_gestao_app python -c "$(cat criar_usuarios_equipe.py)"
"""
import django, os, sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth.models import User
from meigestao_app.usuarios.models import Perfil
from meigestao_app.core.models import Empresa
from datetime import date

EMPRESA_NOME = "JR Solutions Tecnologia"

emp = Empresa.objects.filter(nome__icontains=EMPRESA_NOME).first()
if not emp:
    print("ERRO: empresa nao encontrada"); sys.exit(1)
print("Empresa:", emp.id, emp.nome, "plano=", emp.plano)

# (login, funcao, senha_provisoria)
CRIACAO = [
    ("vendedor_paulo",  "vendedor", "Trocar@123"),
    ("vendedor_carlos", "vendedor", "Trocar@123"),
    ("operador_maria",  "operador", "Trocar@123"),
]

LIMITE = {"basico": 2, "profissional": 5, "enterprise": 20}.get(emp.plano, 5)
jausados = Perfil.objects.filter(empresa=emp).count()
print(f"Limite do plano: {LIMITE} | ja usados: {jausados} | vagas: {LIMITE - jausados}")

if jausados + len(CRIACAO) > LIMITE:
    print(f"ERRO: criacao de {len(CRIACAO)} estoura o limite ({jausados}+{len(CRIACAO)}>{LIMITE})")
    sys.exit(1)

criados = []
for login, funcao, senha in CRIACAO:
    u = User.objects.filter(username=login).first()
    if u:
        print(f"  [ja existe] {login}")
        continue
    u = User.objects.create_user(username=login, password=senha, is_staff=False, is_superuser=False)
    Perfil.objects.create(
        usuario=u, empresa=emp, permissao=funcao,
        data_admissao=date.today(), ativo=True,
    )
    criados.append((login, funcao, senha))
    print(f"  [criado] {login:20s} | {funcao:10s} | senha= {senha}")

print("\n=== RESUMO ===")
for c in criados:
    print(f"  login={c[0]:20s} | funcao={c[1]:10s} | senha_provisoria={c[2]}")
print(f"\nTotal criados agora: {len(criados)}")
print(f"Perfis na empresa agora: {Perfil.objects.filter(empresa=emp).count()}/{LIMITE}")
