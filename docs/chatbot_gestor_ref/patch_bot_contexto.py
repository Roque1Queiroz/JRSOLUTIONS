# -*- coding: utf-8 -*-
"""Insere a funcao bot_contexto no views.py da VM (patch minimo)."""
p = "/home/ubuntu/Sistema_Gestor/meigestao_app/core/views.py"
s = open(p, encoding="utf-8").read()

anchor = "return render(request, 'dashboard.html', context)"
assert s.count(anchor) == 1, "anchor nao unica: %d" % s.count(anchor)

func = '''

@login_required
def bot_contexto(request):
    """
    Endpoint apenas-leitura que alimenta o assistente de IA (chatbot) com dados
    reais e agregados da EMPRESA do usuário logado.

    Segurança: exige autenticação; usa get_empresa_do_usuario (nunca all());
    NÃO devolve dados sensíveis (CPF/CNPJ, senhas, contas), apenas agregados.
    """
    from django.http import JsonResponse

    empresa = get_empresa_do_usuario(request.user)
    if not empresa:
        return JsonResponse({"erro": "Empresa não identificada."}, status=403)

    hoje = timezone.now()
    inicio_mes = hoje.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    inicio_hoje = hoje.replace(hour=0, minute=0, second=0, microsecond=0)

    vendas_qs = Venda.objects.filter(empresa=empresa)
    # Faturamento = soma de vendas CONFIRMADAS (mesma regra do dashboard).
    faturamento_mes = (
        vendas_qs.filter(data_venda__gte=inicio_mes, status="confirmada")
        .aggregate(Sum("valor_total"))["valor_total__sum"]
        or 0
    )
    faturamento_hoje = (
        vendas_qs.filter(data_venda__gte=inicio_hoje, status="confirmada")
        .aggregate(Sum("valor_total"))["valor_total__sum"]
        or 0
    )
    total_vendas_mes = vendas_qs.filter(data_venda__gte=inicio_mes).exclude(status="cancelada").count()
    vendas_pendentes = vendas_qs.filter(status="rascunho", data_venda__gte=inicio_mes).count()

    return JsonResponse({
        "empresa": empresa.nome,
        "faturamento_mes": float(faturamento_mes),
        "faturamento_hoje": float(faturamento_hoje),
        "total_vendas_mes": total_vendas_mes,
        "vendas_pendentes": vendas_pendentes,
        "nota": "Dados agregados apenas desta empresa, filtrados pelo usuário autenticado.",
    })
'''

s = s.replace(anchor, anchor + func, 1)
open(p, "w", encoding="utf-8").write(s)
print("OK: bot_contexto inserido na VM")
