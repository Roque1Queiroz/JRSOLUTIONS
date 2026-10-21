# -*- coding: utf-8 -*-
"""Regras puras do nosso boleto (conta parcelada). Sem juros."""

import calendar
from datetime import date
from decimal import Decimal, ROUND_DOWN


def dividir_valor(total, numero_parcelas):
    """Parcelas iguais. A sobra de centavo fica na última."""
    total = Decimal(total).quantize(Decimal('0.01'))
    n = int(numero_parcelas)
    if n < 1:
        raise ValueError('numero_parcelas invalido')
    base = (total / Decimal(n)).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
    valores = [base] * (n - 1)
    ultima = (total - base * (n - 1)).quantize(Decimal('0.01'))
    valores.append(ultima)
    return valores


def somar_meses(data_inicial, meses):
    """Mesmo dia nos meses seguintes. Dia inexistente cai no último do mês."""
    if not isinstance(data_inicial, date):
        raise TypeError('data_inicial deve ser date')
    indice = data_inicial.month - 1 + int(meses)
    ano = data_inicial.year + indice // 12
    mes = indice % 12 + 1
    ultimo = calendar.monthrange(ano, mes)[1]
    return date(ano, mes, min(data_inicial.day, ultimo))


def referencia_parcela(compromisso_id, numero):
    return 'NB-{0}-{1:02d}'.format(compromisso_id, int(numero))
