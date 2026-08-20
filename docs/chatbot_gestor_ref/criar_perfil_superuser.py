# -*- coding: utf-8 -*-
"""Cria/garante o perfil (funcao admin + empresa) do superuser JRSolutionsRoque."""
import django, os, sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth.models import User
from meigestao_app.usuarios.models import Perfil
from meigestao_app.core.models import Empresa
from datetime import date

USERNAME = "JRSolutionsRoque"

u = User.objects.filter(username=USERNAME).first()
if not u:
    print("ERRO: usuario nao existe"); sys.exit(1)

print("Empresas disponiveis:")
for e in Empresa.objects.all().order_by("id"):
    print(f"  id={e.id} | {e.nome} | plano={e.plano}")

emp = Empresa.objects.filter(nome__icontains="JR Solutions Tecnologia").first() or \
      Empresa.objects.filter(plano="profissional").first() or \
      Empresa.objects.filter(plano="enterprise").first() or \
      Empresa.objects.first()
print("Empresa escolhida:", emp.id, emp.nome, emp.plano if emp else None)

if Perfil.objects.filter(usuario=u).exists():
    p = Perfil.objects.get(usuario=u)
    p.permissao = "admin"
    p.empresa = emp
    p.ativo = True
    if not p.data_admissao:
        p.data_admissao = date.today()
    p.save()
    print("Perfil ATUALIZADO p/ admin; id perfil=", p.id)
else:
    p = Perfil.objects.create(
        usuario=u, empresa=emp, permissao="admin",
        data_admissao=date.today(), ativo=True,
    )
    print("Perfil CRIADO p/ admin; id perfil=", p.id)

p = Perfil.objects.get(usuario=u)
print("CONFIRMACAO: user=", u.username, "| funcao=", p.permissao,
      "| empresa=", p.empresa.nome if p.empresa else None, "| ativo=", p.ativo)
