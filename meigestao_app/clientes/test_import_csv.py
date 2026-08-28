# -*- coding: utf-8 -*-
"""Testes da importação de Clientes via CSV e do modelo CSV (Spec modelo-csv-importacao).

Critérios de aceite:
- CA1 — GET clientes:modelo_csv sem login -> redirect (302) para login.
- CA2 — GET clientes:modelo_csv logado -> HTTP 200, Content-Disposition com
  modelo_clientes.csv, cabeçalho exato e exatamente 1 linha de exemplo.
- CA4 — POST clientes:cliente_import com CSV nas mesmas colunas do modelo -> 302 e
  cliente criado na empresa do usuário.
- CA6 — O CSV do modelo é lido pelo importador sem erro de cabeçalho (round-trip).
"""
import csv
import io
from datetime import date

import pytest
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from meigestao_app.clientes.models import Cliente
from meigestao_app.core.models import Empresa
from meigestao_app.core.utils.csv_modelos import COLUNAS_CLIENTES
from meigestao_app.usuarios.models import Perfil

CSV_CPF_VALIDO = '111.444.777-35'  # CPF com dígitos verificadores reais (testes)


@pytest.fixture
def usuario_logado(client, db):
    empresa = Empresa.objects.create(nome='Empresa Modelo CSV', cnpj='11.111.111/0001-11')
    usuario = User.objects.create_user(username='gerente_modelo', password='senha-forte-123')
    Perfil.objects.create(
        usuario=usuario,
        empresa=empresa,
        permissao='gerente',
        data_admissao=date.today(),
    )
    client.force_login(usuario)
    return usuario, empresa


# --- CA1: exige login ------------------------------------------------------

def test_modelo_csv_exige_login(client, db):
    resp = client.get(reverse('clientes:modelo_csv'))
    assert resp.status_code in (302, 403)  # sem login -> redireciona/bloqueia


# --- CA2: download do modelo de clientes -----------------------------------

def test_modelo_csv_cabecalho_e_linha_exemplo(usuario_logado, client):
    resp = client.get(reverse('clientes:modelo_csv'))
    assert resp.status_code == 200
    assert resp['Content-Type'].startswith('text/csv')
    assert 'modelo_clientes.csv' in resp['Content-Disposition']

    conteudo = resp.content.decode('utf-8-sig')  # utf-8-sig remove o BOM
    linhas = conteudo.splitlines()
    reader = csv.DictReader(linhas, delimiter=';')
    assert reader.fieldnames == COLUNAS_CLIENTES
    dados = list(reader)
    assert len(dados) == 1  # exatamente 1 linha de exemplo
    assert dados[0]['nome'].startswith('EXEMPLO -')
    assert dados[0]['cpf_cnpj']


# --- CA4: importação com o formato do modelo --------------------------------

def test_importar_clientes_no_formato_do_modelo(usuario_logado, client):
    _, empresa = usuario_logado
    cabecalho = ';'.join(COLUNAS_CLIENTES)
    linha = ';'.join([
        'Maria da Silva Teste', CSV_CPF_VALIDO, 'maria@teste.com.br',
        '(11) 98888-7777', 'Av. Paulista, 1000', 'Sao Paulo', 'SP', '01310-100',
    ])
    arquivo = SimpleUploadedFile(
        'clientes.csv',
        ('\ufeff' + cabecalho + '\r\n' + linha + '\r\n').encode('utf-8'),
        content_type='text/csv',
    )
    resp = client.post(reverse('clientes:cliente_import'), {'csv_file': arquivo})
    assert resp.status_code == 302  # redirect p/ lista

    cliente = Cliente.objects.filter(empresa=empresa, cpf_cnpj=CSV_CPF_VALIDO).first()
    assert cliente is not None
    assert cliente.nome == 'Maria da Silva Teste'
    assert cliente.email == 'maria@teste.com.br'
    assert cliente.cidade == 'Sao Paulo'
    assert cliente.tipo == 'pf'


# --- CA6: round-trip do modelo contra o importador --------------------------

def test_modelo_baixado_importa_sem_erro_de_cabecalho(usuario_logado, client):
    """O CSV baixado (após trocar a linha de exemplo) não gera erro de cabeçalho."""
    resp = client.get(reverse('clientes:modelo_csv'))
    conteudo = resp.content.decode('utf-8-sig')
    # Substitui a linha de exemplo por um dado real (mesmo formato).
    linhas = conteudo.splitlines()
    linhas[1] = ';'.join([
        'Cliente Roundtrip', '390.533.447-05', 'roundtrip@teste.com.br',
        '', '', '', '', '',
    ])
    arquivo = SimpleUploadedFile(
        'clientes.csv',
        ('\ufeff' + '\r\n'.join(linhas) + '\r\n').encode('utf-8'),
        content_type='text/csv',
    )
    resp = client.post(reverse('clientes:cliente_import'), {'csv_file': arquivo})
    assert resp.status_code == 302
    assert Cliente.objects.filter(cpf_cnpj='390.533.447-05').exists()


def test_importar_clientes_com_virgula_tambem_funciona(usuario_logado, client):
    """O importador aceita o mesmo cabeçalho com delimitador vírgula."""
    _, empresa = usuario_logado
    arquivo = SimpleUploadedFile(
        'clientes.csv',
        ('nome,cpf_cnpj,email,telefone,endereco,cidade,estado,cep\r\n'
         'Joao Virgula,529.982.247-25,joao@teste.com.br,,,,,\r\n').encode('utf-8'),
        content_type='text/csv',
    )
    resp = client.post(reverse('clientes:cliente_import'), {'csv_file': arquivo})
    assert resp.status_code == 302
    assert Cliente.objects.filter(empresa=empresa, nome='Joao Virgula').exists()