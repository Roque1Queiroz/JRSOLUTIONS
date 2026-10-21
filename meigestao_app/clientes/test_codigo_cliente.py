# -*- coding: utf-8 -*-
import threading
from datetime import date

import pytest
from django.contrib.auth.models import User
from django.db import connection
from django.urls import reverse

from meigestao_app.clientes.models import Cliente
from meigestao_app.core.models import Empresa
from meigestao_app.usuarios.models import Perfil
from meigestao_app.vendas.models import Venda


def _empresa(nome, cnpj):
    return Empresa.objects.create(nome=nome, cnpj=cnpj, plano='enterprise')


def _usuario(username, empresa):
    user = User.objects.create_user(username=username, password='senha-forte-de-teste', is_staff=False)
    Perfil.objects.create(
        usuario=user,
        empresa=empresa,
        permissao='admin',
        data_admissao=date.today(),
    )
    return user


def _cliente(empresa, nome, doc):
    return Cliente.objects.create(
        empresa=empresa,
        nome=nome,
        tipo='pf',
        cpf_cnpj=doc,
    )


@pytest.mark.django_db
def test_ca1_primeiro_cliente_mostra_01_sem_id_interno(client):
    empresa = _empresa('Cli A1', '91.000.000/0001-91')
    user = _usuario('cli_a1', empresa)
    outro = _empresa('Cli Sobra', '91.000.000/0001-99')
    _cliente(outro, 'Sobra para subir o id', '910.000.000-91')
    cliente = _cliente(empresa, 'Primeiro da A', '910.000.000-01')
    assert cliente.codigo == 1
    assert cliente.id != 1
    client.force_login(user)
    response = client.get(reverse('clientes:cliente_list'))
    html = response.content.decode()
    assert response.status_code == 200
    assert '#01' in html
    assert '>#{0}<'.format(cliente.id) not in html
    assert 'Código' in html or 'Codigo' in html


@pytest.mark.django_db
def test_ca2_segundo_cliente_codigo_2():
    empresa = _empresa('Cli A2', '91.000.000/0001-92')
    _cliente(empresa, 'Um', '910.000.000-11')
    segundo = _cliente(empresa, 'Dois', '910.000.000-12')
    assert segundo.codigo == 2


@pytest.mark.django_db
def test_ca3_outra_empresa_tambem_comeca_em_1():
    empresa_a = _empresa('Cli A3', '91.000.000/0001-93')
    empresa_b = _empresa('Cli B3', '91.000.000/0001-94')
    _cliente(empresa_a, 'A', '910.000.000-21')
    primeiro_b = _cliente(empresa_b, 'B', '910.000.000-22')
    assert primeiro_b.codigo == 1


@pytest.mark.django_db
def test_ca4_apagar_nao_reusa_codigo():
    empresa = _empresa('Cli A4', '91.000.000/0001-95')
    primeiro = _cliente(empresa, 'Sai', '910.000.000-31')
    assert primeiro.codigo == 1
    primeiro.delete()
    seguinte = _cliente(empresa, 'Entra', '910.000.000-32')
    assert seguinte.codigo == 2


@pytest.mark.django_db
def test_ca5_venda_mostra_codigo_e_nao_id_cadastro(client):
    empresa = _empresa('Cli A5', '91.000.000/0001-96')
    user = _usuario('cli_a5', empresa)
    outro = _empresa('Cli Sobra 5', '91.000.000/0001-89')
    _cliente(outro, 'Sobra', '910.000.000-40')
    cliente = _cliente(empresa, 'Comprador', '910.000.000-41')
    venda = Venda.objects.create(empresa=empresa, cliente=cliente, status='rascunho')
    client.force_login(user)
    response = client.get(reverse('vendas:venda_detail', kwargs={'pk': venda.pk}))
    html = response.content.decode()
    assert response.status_code == 200
    assert '#01' in html or '01' in html
    assert 'ID Cadastro' not in html
    assert 'ID Cadastro: {0}'.format(cliente.id) not in html


@pytest.mark.django_db(transaction=True)
def test_ca6_cadastros_simultaneos_nao_repetem_codigo():
    empresa = _empresa('Cli A6', '91.000.000/0001-97')
    erros = []
    prontos = threading.Barrier(2)

    def criar(indice):
        try:
            prontos.wait(timeout=5)
            Cliente.objects.create(
                empresa=empresa,
                nome='Paralelo {0}'.format(indice),
                tipo='pf',
                cpf_cnpj='910.000.000-5{0}'.format(indice),
            )
        except Exception as exc:
            erros.append(repr(exc))
        finally:
            connection.close()

    fios = [threading.Thread(target=criar, args=(i,)) for i in (1, 2)]
    for fio in fios:
        fio.start()
    for fio in fios:
        fio.join(timeout=15)
    codigos = list(Cliente.objects.filter(empresa=empresa).values_list('codigo', flat=True))
    assert erros == [], erros
    assert sorted(codigos) == [1, 2]
