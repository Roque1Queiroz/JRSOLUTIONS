# -*- coding: utf-8 -*-
"""Aplica o menu condicional por modulos_permitidos no base.html da VM (idempotente)."""
p = "/home/ubuntu/Sistema_Gestor/templates/base.html"
s = open(p, encoding="utf-8").read()
orig = s
changes = []

def sub(old, new, tag):
    global s, changes
    if old in s and new not in s:
        assert s.count(old) == 1, "anchor nao unica: " + tag
        s = s.replace(old, new, 1)
        changes.append(tag)
    else:
        changes.append(tag + " (skip já aplicado/inexistente)")

# Clientes
sub(
    '<ul class="nav flex-column mb-3">\n            <li class="nav-item">\n                <a class="nav-link {% if \'clientes\' in request.path %}active{% endif %}"\n                    href="{% url \'clientes:cliente_list\' %}">',
    '<ul class="nav flex-column mb-3">\n            {% if \'clientes\' in modulos_permitidos %}\n            <li class="nav-item">\n                <a class="nav-link {% if \'clientes\' in request.path %}active{% endif %}"\n                    href="{% url \'clientes:cliente_list\' %}">',
    'clientes-abre'
)
sub(
    '<i class="bi bi-people"></i> Gestão de Clientes\n                </a>\n            </li>\n            <li class="nav-item">\n                <a class="nav-link {% if \'vendas\' in request.path %}active{% endif %}"\n                    href="{% url \'vendas:venda_list\' %}">',
    '<i class="bi bi-people"></i> Gestão de Clientes\n                </a>\n            </li>\n            {% endif %}\n            {% if \'vendas\' in modulos_permitidos %}\n            <li class="nav-item">\n                <a class="nav-link {% if \'vendas\' in request.path %}active{% endif %}"\n                    href="{% url \'vendas:venda_list\' %}">',
    'clientes-fecha-vendas-abre'
)
# Fecha vendas e abre estoque seção
sub(
    '<i class="bi bi-bag-check"></i> Gestão de Vendas\n                </a>\n            </li>\n        </ul>\n\n        <span class="sidebar-section">Gestão de Estoque</span>',
    '<i class="bi bi-bag-check"></i> Gestão de Vendas\n                </a>\n            </li>\n            {% endif %}\n        </ul>\n\n        {% if \'estoque\' in modulos_permitidos %}\n        <span class="sidebar-section">Gestão de Estoque</span>',
    'vendas-fecha-estoque-secao'
)
sub(
    '<i class="bi bi-box-seam"></i> Gestão de Produtos\n                </a>\n            </li>\n            {% if empresa_obj.plano != \'basico\' %}',
    '<i class="bi bi-box-seam"></i> Gestão de Produtos\n                </a>\n            </li>\n            {% if empresa_obj.plano != \'basico\' and \'almoxarifado\' in modulos_permitidos %}',
    'almoxarifado-cond'
)
# Fecha estoque seção, abre operacional com producao
sub(
    '{% endif %}\n        </ul>\n\n        {% if empresa_obj.plano != \'basico\' %}\n        <span class="sidebar-section">Gestão Operacional</span>',
    '{% endif %}\n        </ul>\n        {% endif %}\n\n        {% if empresa_obj.plano != \'basico\' and \'producao\' in modulos_permitidos %}\n        <span class="sidebar-section">Gestão Operacional</span>',
    'estoque-fecha-operacional-producao'
)
# Serviços cond
sub(
    'href="{% url \'servicos:dashboard\' %}"\n                    <i class="bi bi-wrench-adjustable"></i> Ordens de Serviço (O.S.)\n                </a>\n            </li>\n            <li class="nav-item">',
    'href="{% url \'servicos:dashboard\' %}"\n                    <i class="bi bi-wrench-adjustable"></i> Ordens de Serviço (O.S.)\n                </a>\n            </li>\n            {% if \'compras\' in modulos_permitidos %}\n            <li class="nav-item">',
    'servicos-compras'
)
sub(
    'href="{% url \'producao:dashboard\' %}"\n                    <i class="bi bi-gear-wide-connected"></i> Gestão de Produção (PCP)\n                </a>\n            </li>\n            <li class="nav-item">',
    'href="{% url \'producao:dashboard\' %}"\n                    <i class="bi bi-gear-wide-connected"></i> Gestão de Produção (PCP)\n                </a>\n            </li>\n            {% if \'servicos\' in modulos_permitidos %}\n            <li class="nav-item">',
    'producao-servicos'
)
sub(
    '<i class="bi bi-cart-check"></i> Gestão de Compras\n                </a>\n            </li>\n        </ul>\n        {% endif %}\n\n        <span class="sidebar-section">Gestão Financeira</span>',
    '<i class="bi bi-cart-check"></i> Gestão de Compras\n                </a>\n            </li>\n            {% endif %}\n        </ul>\n        {% endif %}\n\n        {% if \'financeiro\' in modulos_permitidos %}\n        <span class="sidebar-section">Gestão Financeira</span>',
    'compras-fecha-financeiro'
)
sub(
    '</ul>\n\n        {% if empresa_obj.plano != \'basico\' %}\n        <span class="sidebar-section">Gestão Fiscal</span>',
    '</ul>\n        {% endif %}\n\n        {% if empresa_obj.plano != \'basico\' and \'fiscal\' in modulos_permitidos %}\n        <span class="sidebar-section">Gestão Fiscal</span>',
    'financeiro-fecha-fiscal'
)

if s != orig:
    open(p, "w", encoding="utf-8").write(s)
    print("ALTERADO")
else:
    print("SEM MUDANCAS")
for c in changes:
    print(" -", c)
