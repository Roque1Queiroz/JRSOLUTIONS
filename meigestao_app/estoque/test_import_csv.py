# -*- coding: utf-8 -*-
"""Testes da importação de Produtos via CSV e do modelo CSV (Spec modelo-csv-importacao).

Critérios de aceite:
- CA3 — GET estoque:modelo_csv logado -> HTTP 200, Content-Disposition com
  modelo_produtos.csv, cabeçalho exato e exatamente 1 linha de exemplo.
- CA5 — POST estoque:produto_import com CSV nas mesmas colunas do modelo -> 302,
  produto criado, categoria criada/associada, estoque inicial aplicado.
"""
import csv
from datetime import date

import pytest
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from meigestao_app.core.models import Empresa
from meigestao_app.core.utils.csv_modelos import COLUNAS_PRODUTOS
from meigestao_app.estoque.models import Categoria, Estoque, MovimentacaoEstoque, Produto
from meigestao_app.usuarios.models import Perfil


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


# --- CA3: download do modelo de produtos ------------------------------------

def test_modelo_produtos_cabecalho_e_linha_exemplo(usuario_logado, client):
    resp = client.get(reverse('estoque:modelo_csv'))
    assert resp.status_code == 200
    assert resp['Content-Type'].startswith('text/csv')
    assert 'modelo_produtos.csv' in resp['Content-Disposition']

    conteudo = resp.content.decode('utf-8-sig')
    reader = csv.DictReader(conteudo.splitlines(), delimiter=';')
    assert reader.fieldnames == COLUNAS_PRODUTOS
    dados = list(reader)
    assert len(dados) == 1
    assert dados[0]['nome'].startswith('EXEMPLO -')
    assert dados[0]['sku']


def test_modelo_produtos_exige_login(client, db):
    resp = client.get(reverse('estoque:modelo_csv'))
    assert resp.status_code in (302, 403)


# --- CA5: importação com o formato do modelo --------------------------------

def test_importar_produtos_no_formato_do_modelo(usuario_logado, client):
    _, empresa = usuario_logado
    cabecalho = ';'.join(COLUNAS_PRODUTOS)
    linha = ';'.join(['Parafuso Inox M8', 'PAR-001', '2,50', 'Fixadores', '1,20', '40', 'Parafuso 30mm'])
    arquivo = SimpleUploadedFile(
        'produtos.csv',
        ('\ufeff' + cabecalho + '\r\n' + linha + '\r\n').encode('utf-8'),
        content_type='text/csv',
    )
    resp = client.post(reverse('estoque:produto_import'), {'csv_file': arquivo})
    assert resp.status_code == 302

    produto = Produto.objects.filter(empresa=empresa, sku='PAR-001').first()
    assert produto is not None
    assert produto.nome == 'Parafuso Inox M8'
    assert str(produto.preco_venda) == '2.50'  # decimal normalizado
    assert str(produto.preco_custo) == '1.20'

    # Categoria criada automaticamente
    assert Categoria.objects.filter(empresa=empresa, nome='Fixadores').exists()
    assert produto.categoria.nome == 'Fixadores'

    # Estoque inicial aplicado + movimentação de entrada registrada
    estoque = Estoque.objects.filter(produto=produto).first()
    assert estoque is not None
    assert estoque.quantidade == 40
    assert MovimentacaoEstoque.objects.filter(produto=produto, tipo_movimento='entrada').exists()


def test_importar_produto_sem_categoria_usa_geral(usuario_logado, client):
    """Sem a coluna/valor categoria, o sistema usa 'Geral' (comportamento atual)."""
    _, empresa = usuario_logado
    arquivo = SimpleUploadedFile(
        'produtos.csv',
        ('nome;sku;preco_venda;categoria;preco_custo;estoque_inicial;descricao\r\n'
         'Cabo de Aco;CAB-010;35,00;;25,00;2;\r\n').encode('utf-8'),
        content_type='text/csv',
    )
    resp = client.post(reverse('estoque:produto_import'), {'csv_file': arquivo})
    assert resp.status_code == 302
    produto = Produto.objects.filter(empresa=empresa, sku='CAB-010').first()
    assert produto is not None
    assert produto.categoria.nome == 'Geral'