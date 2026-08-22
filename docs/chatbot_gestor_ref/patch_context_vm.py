# -*- coding: utf-8 -*-
"""Adiciona permissoes (funcao_usuario + modulos_permitidos) ao context_processors da VM."""
p = "/home/ubuntu/Sistema_Gestor/meigestao_app/core/context_processors.py"
s = open(p, encoding="utf-8").read()

# imports
if "from meigestao_app.core.mixins import funcao_do_usuario" not in s:
    old_imp = "from meigestao_app.core.models import Empresa"
    new_imp = ("from meigestao_app.core.models import Empresa\n"
               "from meigestao_app.core.mixins import funcao_do_usuario\n"
               "from meigestao_app.core.permissoes import modulos_que_ve")
    assert old_imp in s and s.count(old_imp) == 1
    s = s.replace(old_imp, new_imp, 1)
    print("imports adicionados")

# contexto base
old_ctx = "'empresa_nome': 'SISTEMA GESTOR'"
new_ctx = ("'empresa_nome': 'SISTEMA GESTOR',\n"
           "        'funcao_usuario': None,\n"
           "        'modulos_permitidos': [],")
assert old_ctx in s and s.count(old_ctx) == 1
if "'funcao_usuario'" not in s:
    s = s.replace(old_ctx, new_ctx, 1)
    print("contexto-base adicionado")

# injeta permissões antes de `return context`
if "modulos_permitidos'] = sorted" not in s:
    old_ret = "'reembolsos_pendentes_count'] = pendentes"
    new_ret = ("'reembolsos_pendentes_count'] = pendentes\n"
               "\n"
               "        func = funcao_do_usuario(request.user)\n"
               "        context['funcao_usuario'] = func or ('' if request.user.is_staff else 'operador')\n"
               "        context['modulos_permitidos'] = sorted(modulos_que_ve(func) if func else [])")
    assert old_ret in s and s.count(old_ret) == 1, "anchor reembolsos nao unica"
    s = s.replace(old_ret, new_ret, 1)
    print("permissoes injetadas")

open(p, "w", encoding="utf-8").write(s)
print("FEITO")
