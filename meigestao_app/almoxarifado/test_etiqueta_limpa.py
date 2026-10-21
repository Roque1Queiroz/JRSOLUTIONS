# -*- coding: utf-8 -*-
from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from meigestao_app.almoxarifado.models import EnderecoArmazenamento, LocalArmazenamento, SaldoAlmoxarifado
from meigestao_app.core.models import Empresa
from meigestao_app.estoque.models import Categoria, Produto
from meigestao_app.usuarios.models import Perfil


def _empresa(nome, cnpj):
    return Empresa.objects.create(nome=nome, cnpj=cnpj, plano='profissional')


def _usuario(username, empresa):
    user = User.objects.create_user(username=username, password='senha-forte-de-teste', is_staff=False)
    Perfil.objects.create(
        usuario=user,
        empresa=empresa,
        permissao='admin',
        data_admissao=date.today(),
    )
    return user


def _peca(empresa, sku, nome, local_nome, saldo, minimo, codigo_endereco):
    categoria = Categoria.objects.create(empresa=empresa, nome='Geral ' + sku)
    produto = Produto.objects.create(
        empresa=empresa,
        categoria=categoria,
        nome=nome,
        sku=sku,
        preco_custo=Decimal('1.00'),
        preco_venda=Decimal('2.00'),
    )
    local = LocalArmazenamento.objects.create(empresa=empresa, nome=local_nome, ativo=True)
    endereco = EnderecoArmazenamento.objects.create(local=local, codigo_endereco=codigo_endereco)
    SaldoAlmoxarifado.objects.create(
        local=local,
        endereco=endereco,
        produto=produto,
        quantidade=saldo,
        quantidade_minima=minimo,
    )
    return produto, local, endereco


@pytest.mark.django_db
def test_ca1_etiqueta_so_qr_e_sku(client):
    empresa = _empresa('Almox Etiq', '81.000.000/0001-81')
    user = _usuario('almox_etiq', empresa)
    produto, _, _ = _peca(
        empresa, 'SKU-CAIXA-01', 'Nome que nao pode ir na etiqueta',
        'Galpao', Decimal('4.00'), Decimal('1.00'), 'END-CAIXA-01',
    )
    client.force_login(user)
    response = client.get(reverse('almoxarifado:central_etiquetas'))
    assert response.status_code == 200
    html = response.content.decode()
    assert produto.sku in html
    assert '/almoxarifado/peca/' in html
    inicio = html.find('class="etiqueta-peca"')
    assert inicio != -1
    fim = html.find('etiqueta-peca-fim', inicio)
    bloco = html[inicio:fim]
    assert produto.nome not in bloco
    assert produto.sku in bloco


@pytest.mark.django_db
def test_ca2_ficha_mostra_nome_local_saldo_minimo(client):
    empresa = _empresa('Almox Ficha', '81.000.000/0001-82')
    user = _usuario('almox_ficha', empresa)
    produto, local, _ = _peca(
        empresa, 'SKU-FICHA-02', 'Parafuso Ficha',
        'Galpao Norte', Decimal('7.50'), Decimal('2.00'), 'END-FICHA-02',
    )
    client.force_login(user)
    response = client.get(reverse('almoxarifado:peca_view', kwargs={'sku': produto.sku}))
    assert response.status_code == 200
    html = response.content.decode()
    assert produto.nome in html
    assert local.nome in html
    assert '7.50' in html
    assert '2.00' in html


@pytest.mark.django_db
def test_ca3_outra_empresa_nao_ve_saldo(client):
    empresa_a = _empresa('Almox Dona', '81.000.000/0001-83')
    empresa_b = _empresa('Almox Alheia', '81.000.000/0001-84')
    user_b = _usuario('almox_alheia', empresa_b)
    produto, _, _ = _peca(
        empresa_a, 'SKU-ALHEIO-03', 'Peca da A',
        'Deposito A', Decimal('19.00'), Decimal('3.00'), 'END-ALHEIO-03',
    )
    client.force_login(user_b)
    response = client.get(reverse('almoxarifado:peca_view', kwargs={'sku': produto.sku}))
    assert response.status_code == 404
    assert '19.00' not in response.content.decode()


@pytest.mark.django_db
def test_ca4_anonimo_nao_recebe_ficha(client):
    empresa = _empresa('Almox Anon', '81.000.000/0001-85')
    produto, _, _ = _peca(
        empresa, 'SKU-ANON-04', 'Peca anonima',
        'Sala', Decimal('1.00'), Decimal('0.00'), 'END-ANON-04',
    )
    response = client.get(reverse('almoxarifado:peca_view', kwargs={'sku': produto.sku}))
    assert response.status_code == 302
    assert 'entrar' in response.url or 'login' in response.url
    assert produto.nome not in response.content.decode()


@pytest.mark.django_db
def test_ca5_prateleira_continua_igual(client):
    empresa = _empresa('Almox Prat', '81.000.000/0001-86')
    user = _usuario('almox_prat', empresa)
    _, _, endereco = _peca(
        empresa, 'SKU-PRAT-05', 'Peca prat',
        'Corredor', Decimal('1.00'), Decimal('0.00'), 'PRAT-CONTINUA-05',
    )
    client.force_login(user)
    response = client.get(reverse('almoxarifado:prateleira_view', kwargs={'codigo': endereco.codigo_endereco}))
    assert response.status_code == 200
    assert endereco.codigo_endereco in response.content.decode()
