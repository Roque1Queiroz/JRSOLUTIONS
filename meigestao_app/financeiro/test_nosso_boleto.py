# -*- coding: utf-8 -*-
from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.urls import reverse

from meigestao_app.core.models import Empresa
from meigestao_app.financeiro.models import CompromissoParcelado, ParcelaCompromisso, Transacao
from meigestao_app.financeiro.parcelas import somar_meses
from meigestao_app.usuarios.models import Perfil


def _empresa(nome, cnpj, plano='enterprise'):
    return Empresa.objects.create(nome=nome, cnpj=cnpj, plano=plano)


def _usuario(username, empresa, permissao='admin', staff=False):
    user = User.objects.create_user(username=username, password='senha-forte-de-teste', is_staff=staff)
    Perfil.objects.create(
        usuario=user,
        empresa=empresa,
        permissao=permissao,
        data_admissao=date.today(),
    )
    return user


@pytest.mark.django_db
def test_ca1_parcelas_centavo_e_fim_de_mes(client):
    empresa = _empresa('Fin CA1', '71.000.000/0001-71')
    user = _usuario('fin_ca1', empresa, 'gerente')
    client.force_login(user)
    response = client.post(reverse('financeiro:compromisso_criar'), {
        'descricao': 'Emprestimo bancada',
        'credor': 'Banco Teste',
        'valor_total': '100.00',
        'numero_parcelas': '3',
        'primeiro_vencimento': '2025-01-31',
        'observacao': '',
    })
    assert response.status_code == 302
    compromisso = CompromissoParcelado.objects.get(descricao='Emprestimo bancada')
    parcelas = list(compromisso.parcelas.order_by('numero'))
    assert [p.valor for p in parcelas] == [Decimal('33.33'), Decimal('33.33'), Decimal('33.34')]
    assert [p.vencimento for p in parcelas] == [
        date(2025, 1, 31),
        date(2025, 2, 28),
        date(2025, 3, 31),
    ]
    assert somar_meses(date(2024, 1, 31), 1) == date(2024, 2, 29)


@pytest.mark.django_db
def test_ca2_soma_igual_ao_total():
    empresa = _empresa('Fin CA2', '71.000.000/0001-72')
    compromisso = CompromissoParcelado.objects.create(
        empresa=empresa,
        descricao='Compra a prazo',
        valor_total=Decimal('100.00'),
        numero_parcelas=3,
        primeiro_vencimento=date(2025, 1, 31),
    )
    soma = sum((p.valor for p in compromisso.parcelas.all()), Decimal('0'))
    assert soma == compromisso.valor_total


@pytest.mark.django_db
def test_ca3_recusa_uma_parcela_121_e_valor_zero():
    empresa = _empresa('Fin CA3', '71.000.000/0001-73')
    base = dict(
        empresa=empresa,
        descricao='Invalido',
        primeiro_vencimento=date(2025, 1, 31),
    )
    with pytest.raises(ValidationError):
        CompromissoParcelado.objects.create(valor_total=Decimal('10.00'), numero_parcelas=1, **base)
    with pytest.raises(ValidationError):
        CompromissoParcelado.objects.create(valor_total=Decimal('10.00'), numero_parcelas=121, **base)
    with pytest.raises(ValidationError):
        CompromissoParcelado.objects.create(valor_total=Decimal('0.00'), numero_parcelas=2, **base)


@pytest.mark.django_db
def test_ca4_isolamento_entre_empresas(client):
    empresa_a = _empresa('Fin A', '71.000.000/0001-74')
    empresa_b = _empresa('Fin B', '71.000.000/0001-75')
    user_a = _usuario('fin_a', empresa_a, 'admin')
    compromisso_b = CompromissoParcelado.objects.create(
        empresa=empresa_b,
        descricao='Segredo empresa B',
        credor='Credor B',
        valor_total=Decimal('50.00'),
        numero_parcelas=2,
        primeiro_vencimento=date(2025, 4, 10),
    )
    parcela_b = compromisso_b.parcelas.order_by('numero').first()
    client.force_login(user_a)
    lista = client.get(reverse('financeiro:compromisso_lista'))
    assert lista.status_code == 200
    assert 'Segredo empresa B' not in lista.content.decode()
    detalhe = client.get(reverse('financeiro:compromisso_detalhe', kwargs={'pk': compromisso_b.pk}))
    assert detalhe.status_code == 404
    boleto = client.get(reverse('financeiro:nosso_boleto', kwargs={
        'pk': compromisso_b.pk,
        'parcela_id': parcela_b.pk,
    }))
    assert boleto.status_code == 404


@pytest.mark.django_db
def test_ca5_vendedor_recebe_403_ao_criar(client):
    empresa = _empresa('Fin Vend', '71.000.000/0001-76')
    vendedor = _usuario('fin_vend', empresa, 'vendedor', staff=False)
    client.force_login(vendedor)
    response = client.post(reverse('financeiro:compromisso_criar'), {
        'descricao': 'Nao pode',
        'credor': '',
        'valor_total': '20.00',
        'numero_parcelas': '2',
        'primeiro_vencimento': '2025-05-01',
    })
    assert response.status_code == 403
    assert CompromissoParcelado.objects.filter(descricao='Nao pode').count() == 0


@pytest.mark.django_db
def test_ca6_marcar_e_desmarcar_paga_liga_despesa(client):
    empresa = _empresa('Fin Paga', '71.000.000/0001-77')
    user = _usuario('fin_paga', empresa, 'gerente')
    compromisso = CompromissoParcelado.objects.create(
        empresa=empresa,
        descricao='Conta de luz parcelada',
        valor_total=Decimal('40.00'),
        numero_parcelas=2,
        primeiro_vencimento=date(2025, 6, 15),
    )
    parcela = compromisso.parcelas.order_by('numero').first()
    client.force_login(user)
    pago = client.post(reverse('financeiro:parcela_pagar', kwargs={
        'pk': compromisso.pk,
        'parcela_id': parcela.pk,
    }))
    assert pago.status_code == 302
    parcela.refresh_from_db()
    assert parcela.paga is True
    assert parcela.data_pagamento is not None
    assert parcela.transacao_id is not None
    transacao = parcela.transacao
    assert transacao.tipo == 'despesa'
    assert transacao.empresa_id == empresa.id
    assert transacao.valor == parcela.valor
    assert transacao.data_vencimento == parcela.vencimento
    assert transacao.paga is True
    transacao_id = transacao.id
    desmarcado = client.post(reverse('financeiro:parcela_pagar', kwargs={
        'pk': compromisso.pk,
        'parcela_id': parcela.pk,
    }))
    assert desmarcado.status_code == 302
    parcela.refresh_from_db()
    transacao.refresh_from_db()
    assert parcela.paga is False
    assert transacao.paga is False
    assert Transacao.objects.filter(pk=transacao_id).exists()


@pytest.mark.django_db
def test_ca7_nao_exclui_com_parcela_paga(client):
    empresa = _empresa('Fin Del', '71.000.000/0001-78')
    user = _usuario('fin_del', empresa, 'admin')
    compromisso = CompromissoParcelado.objects.create(
        empresa=empresa,
        descricao='Nao apagar',
        valor_total=Decimal('20.00'),
        numero_parcelas=2,
        primeiro_vencimento=date(2025, 7, 1),
    )
    parcela = compromisso.parcelas.order_by('numero').first()
    parcela.paga = True
    parcela.save(update_fields=['paga', 'atualizado_em'])
    client.force_login(user)
    response = client.post(reverse('financeiro:compromisso_excluir', kwargs={'pk': compromisso.pk}))
    assert CompromissoParcelado.objects.filter(pk=compromisso.pk).exists()
    assert response.status_code == 302


@pytest.mark.django_db
def test_ca8_folha_tem_referencia_parcela_valor_vencimento_sem_barras(client):
    empresa = _empresa('Fin Folha', '71.000.000/0001-79')
    user = _usuario('fin_folha', empresa, 'admin')
    compromisso = CompromissoParcelado.objects.create(
        empresa=empresa,
        descricao='Folha interna',
        credor='Loja',
        valor_total=Decimal('30.00'),
        numero_parcelas=2,
        primeiro_vencimento=date(2025, 8, 20),
    )
    parcela = compromisso.parcelas.order_by('numero').first()
    client.force_login(user)
    response = client.get(reverse('financeiro:nosso_boleto', kwargs={
        'pk': compromisso.pk,
        'parcela_id': parcela.pk,
    }))
    assert response.status_code == 200
    html = response.content.decode()
    assert parcela.referencia in html
    assert 'parcela {0} de {1}'.format(parcela.numero, compromisso.numero_parcelas) in html
    assert str(parcela.valor) in html or '15,00' in html
    assert parcela.vencimento.strftime('%d/%m/%Y') in html
    baixo = html.lower()
    assert 'código de barras' not in baixo
    assert 'codigo de barras' not in baixo
    assert 'linha digitável' not in baixo
    assert 'linha digitavel' not in baixo
