# -*- coding: utf-8 -*-
"""
Matriz central de permissões por função de usuário (RBAC leve).

Cada usuário tem uma `permissao` no Perfil (admin, gerente, vendedor, operador,
almoxarife, producao). Este módulo concentra, num único lugar, as regras de:

  - QUAIS MÓDULOS o usuário pode VER (abrir);
  - O QUE ele pode ALTERAR/CRIAR e EXCLUIR por módulo.

Assim as views, os templates de menu e os testes usam a MESMA fonte de verdade
(não regras espalhadas). Superusuário/staff do Django tem acesso total e é
tratado antes destas regras.

Paradigma de permissão: "roll-up" por hierarquia. Um usuário também herda as
permissões de todas as funções abaixo da sua na listagem HIERARQUIA_FUNCOES.
"""

# Ordem hierárquica: quanto maior o índice, mais permissões.
HIERARQUIA_FUNCOES = [
    'operador',      # 0 - leitura básica
    'vendedor',      # 1 - pode gerir clientes/vendas
    'almoxarife',    # 2 - pode gerir estoque/almoxarifado/produção e receber compras
    'gerente',       # 3 - visão ampla, gerencia quase tudo
    'admin',         # 4 - controle total (exceto APIs custom, que é do plano)
    'producao',      # 4b - função funcional de chão de fábrica (igual gerente p/ PCP)
]

# Módulos do sistema identificados pelas rotas/namespaces principais.
MODULOS = {
    'dashboard': {'rotas': ['core:dashboard', 'core:']},
    'clientes': {'rotas': ['clientes:']},
    'vendas': {'rotas': ['vendas:']},
    'estoque': {'rotas': ['estoque:']},
    'almoxarifado': {'rotas': ['almoxarifado:']},
    'financeiro': {'rotas': ['financeiro:']},
    'fiscal': {'rotas': ['fiscal:']},
    'compras': {'rotas': ['compras:']},
    'producao': {'rotas': ['producao:']},
    'servicos': {'rotas': ['servicos:']},
    'relatorios': {'rotas': ['relatorios:']},
    'usuarios': {'rotas': ['usuarios:']},
}

# Ver por função (módulos que a função consegue ABRIR).
# 'todos' = todos os módulos.
VER_MODULOS = {
    'operador': ['dashboard', 'clientes', 'vendas'],
    'vendedor': ['dashboard', 'clientes', 'vendas', 'estoque'],
    'almoxarife': ['dashboard', 'estoque', 'almoxarifado', 'producao', 'compras'],
    'gerente': 'todos',
    'admin': 'todos',
    'producao': ['dashboard', 'producao', 'estoque', 'almoxarifado'],
}

# Alterar/criar por função: módulos onde pode CRIAR e EDITAR registros.
ALTERAR_MODULOS = {
    'operador': [],           # leitura apenas
    'vendedor': ['clientes', 'vendas'],
    'almoxarife': ['estoque', 'almoxarifado', 'producao', 'compras'],
    'gerente': 'todos',
    'admin': 'todos',
    'producao': ['producao', 'estoque', 'almoxarifado'],
}

# Excluir por função: módulos onde pode EXCLUIR registros (mais restritivo).
EXCLUIR_MODULOS = {
    'operador': [],
    'vendedor': [],
    'almoxarife': [],
    'gerente': 'todos',
    'admin': 'todos',
    'producao': [],
}

# Funções que, apesar da hierarquia, não herdam automaticamente (casos especiais).
# 'producao' é funcional: não vira admin por estar no topo da lista.

# Conjunto de funções reconhecidas (validadas contra PERMISSOES_CHOICES).
FUNCOES_VALIDAS = set(HIERARQUIA_FUNCOES)


def modulos_que_ve(func):
    """Retorna o conjunto de módulos que a função pode ver (com roll-up)."""
    if func in ('admin', 'gerente'):
        return set(MODULOS.keys())
    return set(VER_MODULOS.get(func, []))


def modulos_que_altera(func):
    """Retorna o conjunto de módulos onde a função pode criar/editar."""
    if func in ('admin', 'gerente'):
        return set(MODULOS.keys())
    return set(ALTERAR_MODULOS.get(func, []))


def modulos_que_exclui(func):
    """Retorna o conjunto de módulos onde a função pode excluir."""
    if func in ('admin', 'gerente'):
        return set(MODULOS.keys())
    return set(EXCLUIR_MODULOS.get(func, []))


def funcao_pode_ver_modulo(func, modulo):
    """True se a função pode ver módulo. 'todos'/lista já tratado nas funções acima."""
    return modulo in modulos_que_ve(func)


def funcao_pode_alterar_modulo(func, modulo):
    """True se pode criar/editar nesse módulo."""
    return modulo in modulos_que_altera(func)


def funcao_pode_excluir_modulo(func, modulo):
    """True se pode excluir nesse módulo."""
    return modulo in modulos_que_exclui(func)


def hierarquia_valida(func):
    """Verifica se a função existe na hierarquia."""
    return func in FUNCOES_VALIDAS
