# -*- coding: utf-8 -*-
"""Painel executivo de DEMONSTRAÇÃO (módulo isolado — facilita deploy idempotente)."""
import calendar
from datetime import timedelta

from django.db.models import F, Sum
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.clickjacking import xframe_options_exempt

from meigestao_app.financeiro.models import Transacao
from meigestao_app.vendas.models import ItemVenda, Venda


@xframe_options_exempt
def demo_dashboard(request):
    """Painel executivo de DEMONSTRAÇÃO (público, para vender).

    Mostra KPIs + gráfico + DRE com DADOS FICTÍCIOS da empresa demo, sempre
    isolados (nunca dados reais de usuários). GET /demo/, sem login.
    """
    from meigestao_app.core.demo_data import get_demo_empresa

    demo = get_demo_empresa()  # garante o seed (idempotente)
    agora = timezone.now()
    inicio_mes = agora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    vendas_qs = Venda.objects.filter(empresa=demo).exclude(status='cancelada')
    vendas_mes = vendas_qs.filter(
        data_venda__gte=inicio_mes,
        data_venda__lt=(inicio_mes + timedelta(days=32)).replace(day=1),
    )
    faturamento_mes = float(vendas_mes.aggregate(s=Sum('valor_total'))['s'] or 0)
    total_vendas_mes = vendas_mes.count()
    ticket_medio = faturamento_mes / total_vendas_mes if total_vendas_mes else 0
    saldo_caixa = float(demo.contas_bancarias.aggregate(s=Sum('saldo'))['s'] or 0)
    estoque_baixo = demo.estoques.filter(quantidade__lte=F('quantidade_minima')).count()
    clientes_novos = demo.clientes.filter(criado_em__gte=inicio_mes).count()

    # Gráfico comparativo (6 meses)
    labels, valores = [], []
    for off in range(5, -1, -1):
        m = _periodo(agora, off)
        v = float(vendas_qs.filter(
            data_venda__gte=m['inicio'], data_venda__lt=m['fim'],
        ).aggregate(s=Sum('valor_total'))['s'] or 0)
        labels.append(m['label'])
        valores.append(v)

    # Top produtos
    top = list(ItemVenda.objects.filter(venda__empresa=demo)
               .values('produto_nome').annotate(total=Sum('quantidade'))
               .order_by('-total')[:5])

    # Vendas recentes
    vendas_recentes = list(
        vendas_qs.order_by('-data_venda').select_related('cliente')[:5]
    )

    # DRE resumido (mês): receitas x despesas
    receita = float(Transacao.objects.filter(
        empresa=demo, tipo='receita', data_transacao__gte=inicio_mes.date(),
    ).aggregate(s=Sum('valor'))['s'] or 0)
    despesa = float(Transacao.objects.filter(
        empresa=demo, tipo='despesa', data_transacao__gte=inicio_mes.date(),
    ).aggregate(s=Sum('valor'))['s'] or 0)

    return render(request, 'meigestao_app/core/demo_dashboard.html', {
        'empresa': demo,
        'faturamento_mes': faturamento_mes,
        'total_vendas_mes': total_vendas_mes,
        'ticket_medio': ticket_medio,
        'saldo_caixa': saldo_caixa,
        'estoque_baixo': estoque_baixo,
        'clientes_novos': clientes_novos,
        'labels_grafico': labels,
        'dados_faturamento': valores,
        'has_revenue_data': any(v > 0 for v in valores),
        'produtos_populares': top,
        'has_produtos': bool(top),
        'vendas_recentes': vendas_recentes,
        'has_vendas_recentes': bool(vendas_recentes),
        'receita': receita,
        'despesa': despesa,
        'lucro': receita - despesa,
    })


def _periodo(agora, offset_meses):
    """Retorna {inicio, fim, label} de um período mensal 'offset' meses atrás."""
    ano, mes = agora.year, agora.month - offset_meses
    while mes < 1:
        mes += 12
        ano -= 1
    inicio = agora.replace(year=ano, month=mes, day=1, hour=0, minute=0, second=0, microsecond=0)
    ultimo_dia = calendar.monthrange(ano, mes)[1]
    fim = inicio.replace(day=ultimo_dia) + timedelta(days=1)
    return {'inicio': inicio, 'fim': fim, 'label': f"{mes:02d}/{ano % 100}"}
