# -*- coding: utf-8 -*-
"""Integração com a API do Asaas (v3) para cobrança/assinatura.

Usa apenas a biblioteca padrão (urllib) e lê as credenciais de settings.
A autenticação da API do Asaas é feita pelo header `access_token`.
"""
import json
import urllib.request
import urllib.error

from django.conf import settings

# Valor mensal (R$) por plano — mesma tabela da página de venda.
PRECOS = {
    'basico': 79.00,
    'profissional': 199.00,
    'enterprise': 499.00,
}

BILLING_TYPE = 'PIX'
CICLO = 'MONTHLY'


def _headers():
    return {
        'access_token': settings.ASAAS_API_KEY,
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'User-Agent': 'SistemaGestor/1.0',
    }


def _request(method, path, payload=None, timeout=30):
    url = settings.ASAAS_BASE_URL.rstrip('/') + '/' + path.lstrip('/')
    body = json.dumps(payload).encode('utf-8') if payload is not None else None
    req = urllib.request.Request(url, data=body, headers=_headers(), method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            return resp.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as e:
        detail = ''
        try:
            detail = e.read().decode('utf-8')[:500]
        except Exception:
            pass
        raise AsaasError(f'Asaas HTTP {e.code}: {detail}')


class AsaasError(Exception):
    pass


def plano_por_valor(valor):
    """Retorna o identificador do plano a partir do valor cobrado."""
    inverso = {v: k for k, v in PRECOS.items()}
    return inverso.get(float(valor or 0))


def configurado():
    return bool(settings.ASAAS_API_KEY)


def criar_cliente(empresa):
    """Garante um cliente (customer) Asaas para a empresa e salva o id."""
    if not configurado():
        return None
    if empresa.asaas_customer_id:
        return empresa.asaas_customer_id
    payload = {
        'name': (empresa.nome or 'Cliente')[:150],
        'cpfCnpj': (empresa.cnpj or '').replace('.', '').replace('/', '').replace('-', ''),
        'email': empresa.email or '',
        'externalReference': str(empresa.id),
    }
    _, data = _request('POST', 'customers', payload)
    cid = data.get('id')
    if cid:
        empresa.asaas_customer_id = cid
        empresa.save(update_fields=['asaas_customer_id', 'atualizado_em'])
    return cid


def criar_assinatura(empresa, plano):
    """Cria a assinatura mensal do plano no Asaas e guarda o id na empresa."""
    if not configurado() or plano not in PRECOS:
        return None
    cliente = criar_cliente(empresa)
    if not cliente:
        return None
    payload = {
        'customer': cliente,
        'billingType': BILLING_TYPE,
        'value': PRECOS[plano],
        'cycle': CICLO,
        'externalReference': str(empresa.id),
        'description': f'Sistema Gestor - Plano {plano.title()}',
        'enablePaymentLink': True,
    }
    _, data = _request('POST', 'subscriptions', payload)
    sid = data.get('id')
    if sid:
        empresa.asaas_subscription_id = sid
        empresa.save(update_fields=['asaas_subscription_id', 'atualizado_em'])
    return data


def link_de_pagamento(subscription_id):
    """Tenta obter o link de pagamento/checkout da assinatura."""
    try:
        _, data = _request('GET', f'subscriptions/{subscription_id}/paymentLink')
        return data.get('url')
    except AsaasError:
        return None


def status_assinatura(subscription_id):
    """Consulta o status atual da assinatura (para validar o webhook)."""
    if not subscription_id:
        return None
    try:
        _, data = _request('GET', f'subscriptions/{subscription_id}')
        return data
    except AsaasError:
        return None
