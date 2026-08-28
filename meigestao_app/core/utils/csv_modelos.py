# -*- coding: utf-8 -*-
"""
Modelos de CSV para importação (Spec modelo-csv-importacao).

Gera arquivos CSV de modelo (cabeçalho exato + linha de exemplo) para as
importações de Clientes e Produtos, prontos para abrir no Excel BR
(UTF-8 com BOM, delimitador ';' e quebra de linha CRLF).

As views são finas e exigem login (qualquer usuário autenticado); o conteúdo
é estático e genérico — não contém dados de empresa (sem risco multi-tenant).
"""
import csv
import io

from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

# Colunas aceitas pelo importador (clientes/views.py ClienteImportView e
# estoque/views.py ProdutoImportView) — manter em sincronia com elas.
COLUNAS_CLIENTES = ['nome', 'cpf_cnpj', 'email', 'telefone', 'endereco', 'cidade', 'estado', 'cep']
COLUNAS_PRODUTOS = ['nome', 'sku', 'preco_venda', 'categoria', 'preco_custo', 'estoque_inicial', 'descricao']

# Linha de exemplo claramente marcada para o usuário substituir/apagar.
EXEMPLO_CLIENTE = [
    'EXEMPLO - Nome do cliente', '111.444.777-35', 'cliente@exemplo.com',
    '(11) 99999-0000', 'Rua das Flores, 100', 'Mogi das Cruzes', 'SP', '08700-000',
]
EXEMPLO_PRODUTO = [
    'EXEMPLO - Produto', 'SKU-001', '10,00', 'Geral', '7,00', '5', 'Produto de exemplo',
]


def _csv_modelo(nome_arquivo, colunas, linha_exemplo):
    """Monta a HttpResponse CSV do modelo (BOM + ';' + CRLF)."""
    buffer = io.StringIO()
    # BOM UTF-8 para o Excel BR abrir direto; o importador usa utf-8-sig e remove.
    buffer.write('\ufeff')
    writer = csv.writer(buffer, delimiter=';', lineterminator='\r\n')
    writer.writerow(colunas)
    writer.writerow(linha_exemplo)

    response = HttpResponse(buffer.getvalue(), content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{nome_arquivo}"'
    return response


@login_required
def modelo_clientes_csv(request):
    """Modelo CSV da importação de Clientes (clientes:modelo_csv)."""
    return _csv_modelo('modelo_clientes.csv', COLUNAS_CLIENTES, EXEMPLO_CLIENTE)


@login_required
def modelo_produtos_csv(request):
    """Modelo CSV da importação de Produtos (estoque:modelo_csv)."""
    return _csv_modelo('modelo_produtos.csv', COLUNAS_PRODUTOS, EXEMPLO_PRODUTO)