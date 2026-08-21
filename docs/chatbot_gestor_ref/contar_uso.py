# -*- coding: utf-8 -*-
"""Conta Empresas, usuários e uso recente — roda na VM (prod) via:
docker exec -e PYTHONPATH=/app -i mei_gestao_app python /dev/stdin < contar_uso.py
"""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from datetime import timedelta
from django.utils import timezone
from django.db.models import Count
from django.contrib.auth.models import User
from meigestao_app.core.models import Empresa
from meigestao_app.usuarios.models import Perfil

agora = timezone.now()
empresas = Empresa.objects.all()
users = User.objects.all()

print("== EMPRESAS ==")
print("total empresas:", empresas.count())
print("por plano:", dict(empresas.values_list('plano').annotate(c=Count('id')).order_by()) or {})
print("em teste (trial ativo):", empresas.filter(trial_expira_em__isnull=False, trial_expira_em__gte=agora).count())

print("== USUARIOS ==")
print("total usuarios:", users.count())
print("staff/superuser:", users.filter(is_staff=True).count())
print("is_active=False:", users.filter(is_active=False).count())

print("== USO RECENTE (quantos LOGARAM) ==")
for dias in (1, 3, 7, 30):
    print(f"  logaram nos ultimos {dias:>2}d: {users.filter(last_login__gte=agora - timedelta(days=dias)).count()}")
print("criados nas ultimas 24h:", users.filter(date_joined__gte=agora - timedelta(days=1)).count())

print("== USUARIOS POR FUNCAO ==")
print(dict(Perfil.objects.values_list('permissao').annotate(c=Count('id')).order_by()) or {})
