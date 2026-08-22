# -*- coding: utf-8 -*-
"""Dados de demonstração (modo demo) — empresa fictícia + dados de exemplo.

Idempotente: se a empresa demo já existir, retorna sem duplicar.
Nunca chega perto dos dados reais de usuários; usa empresa fixa e isolada.
"""
from datetime import timedelta
from decimal import Decimal

import calendar
import datetime as _dt

from django.contrib.auth.models import User
from django.utils import timezone

from meigestao_app.core.models import Empresa
from meigestao_app.usuarios.models import Perfil

DEMO_CNPJ = "00.000.000/0001-01"
DEMO_EMAIL = "demo@jrsolutions.com.br"
DEMO_SENHA = "demo-forte-123"  # is_active=False: não consegue logar


def _data_venda(offset: int, k: int):
    """Datetime de venda dentro do mês 'offset' meses atrás (dia 5+k)."""
    agora = timezone.now()
    ano, mes = agora.year, agora.month - offset
    while mes < 1:
        mes += 12
        ano -= 1
    ultimo = calendar.monthrange(ano, mes)[1]
    if offset == 0:  # mês atual: nunca no futuro, mas garante estar no mês corrente
        dia = min(5 + k, agora.day, ultimo)
    else:
        dia = min(5 + k, ultimo)
    dt = _dt.datetime(ano, mes, max(dia, 1), 10 + offset, 0)
    return timezone.make_aware(dt)


def seed_demo_db():
    """Cria (ou reusa) a empresa de demonstração com dados de exemplo. Idempotente."""
    from meigestao_app.clientes.models import Cliente
    from meigestao_app.estoque.models import Categoria, Estoque, Produto
    from meigestao_app.financeiro.models import ContaBancaria, Transacao
    from meigestao_app.vendas.models import ItemVenda, Venda

    demo = Empresa.objects.filter(cnpj=DEMO_CNPJ).first()
    if demo:
        return demo

    demo = Empresa.objects.create(
        nome="Empresa Demonstração ME",
        cnpj=DEMO_CNPJ,
        email=DEMO_EMAIL,
        telefone="(11) 99999-0000",
        cidade="Mogi das Cruzes",
        estado="SP",
        ativa=True,
    )
    demo.plano = "enterprise"
    demo.save(update_fields=["plano"])

    # usuário-técnico (sem login real)
    user = User.objects.filter(username=DEMO_EMAIL).first()
    if not user:
        user = User.objects.create_user(
            username=DEMO_EMAIL, email=DEMO_EMAIL,
            password=DEMO_SENHA, first_name="Demonstração", is_active=False,
        )
    Perfil.objects.get_or_create(
        usuario=user, empresa=demo,
        defaults={"permissao": "admin",
                  "data_admissao": timezone.now().date(), "ativo": True},
    )

    # Clientes
    clientes = []
    for i, nome in enumerate(["Comercial Andrade", "Mercado Central", "Auto Peças Rápido",
                              "Padaria Quatro Estações", "Papelaria Nova Era", "Transportadora Vilas"], 1):
        c, _ = Cliente.objects.get_or_create(
            cpf_cnpj=f"00.000.00{i:02d}/0001-{i:02d}",
            defaults={"empresa": demo, "nome": nome, "tipo": "pj",
                      "email": f"contato{i}@exemplo.com", "cidade": "Mogi das Cruzes",
                      "estado": "SP", "ativo": True},
        )
        clientes.append(c)

    # Categorias + Produtos + Estoque
    cat_a, _ = Categoria.objects.get_or_create(empresa=demo, nome="Produtos")
    cat_b, _ = Categoria.objects.get_or_create(empresa=demo, nome="Serviços")
    produtos = []
    itens_def = [
        ("Lavadora Industrial", 1800.00, 2600.00, 22, 6),
        ("Esteira de Rolo", 3200.00, 4600.00, 8, 4),
        ("Motor Redutor 1CV", 700.00, 1250.00, 35, 5),
        ("Cabo de Aço 8mm (rolo)", 420.00, 680.00, 12, 4),
        ("Painel de Comando", 1500.00, 2300.00, 0, 3),   # estoque baixo/zera
        ("Manutenção Preventiva", 0.00, 350.00, 999, 3),  # serviço
    ]
    for nome, custo, venda, qtd, minimo in itens_def:
        p, _ = Produto.objects.get_or_create(
            empresa=demo, nome=nome,
            defaults={"sku": f"DEMO-{len(produtos)+1:03d}", "preco_custo": Decimal(custo),
                      "preco_venda": Decimal(venda),
                      "categoria": cat_a if custo > 0 else cat_b, "ativo": True},
        )
        Estoque.objects.get_or_create(
            produto=p, defaults={"empresa": demo, "quantidade": qtd,
                                 "quantidade_minima": minimo, "localizacao": "Armazém A"},
        )
        produtos.append((p, Decimal(venda)))

    # Vendas (6 meses) para o comparativo + vendas recentes
    for mes_off in range(5, -1, -1):
        n = 3 if mes_off != 0 else 5
        for k in range(n):
            cliente = clientes[(mes_off + k) % len(clientes)]
            produto, preco = produtos[(mes_off + k) % len(produtos)]
            quant = 1 + (k % 3)
            data = _data_venda(mes_off, k)
            venda = Venda.objects.create(
                empresa=demo, cliente=cliente, data_venda=data,
                descricao=f"Venda de demonstração #{mes_off}-{k}",
                status="rascunho",
                valor_subtotal=preco * quant, desconto=Decimal("0.00"),
                valor_total=preco * quant,
            )
            ItemVenda.objects.create(
                venda=venda, produto_nome=produto.nome, produto_vinculado=produto,
                quantidade=quant, preco_unitario=preco, subtotal=preco * quant,
            )

    # Contas + Transações (DRE: receitas x despesas)
    conta, _ = ContaBancaria.objects.get_or_create(
        banco="Banco Demonstração", empresa=demo,
        defaults={"agencia": "0001", "conta": "00000-1", "saldo": Decimal("45820.00"), "ativa": True},
    )
    hoje = timezone.now().date()
    Transacao.objects.get_or_create(
        empresa=demo, descricao="Receita de vendas (demonstração)", tipo="receita",
        categoria="Vendas", data_transacao=hoje,
        defaults={"conta": conta, "valor": Decimal("5240.00"), "paga": True},
    )
    Transacao.objects.get_or_create(
        empresa=demo, descricao="Compra de fornecedores (demonstração)", tipo="despesa",
        categoria="Compras", data_transacao=hoje,
        defaults={"conta": conta, "valor": Decimal("3150.00"), "paga": True},
    )
    return demo


def get_demo_empresa():
    """Empresa demo (garante o seed se necessário)."""
    return seed_demo_db()
