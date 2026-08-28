#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Patch idempotente do modelo CSV de importação (Spec modelo-csv-importacao).
Roda na VM com python3. Pré-requisito: o arquivo novo
meigestao_app/core/utils/csv_modelos.py deve ter sido enviado via scp antes.
"""
import datetime
import os
import shutil
import sys

BASE = '/home/ubuntu/Sistema_Gestor'
TODAY = datetime.date.today().strftime('%Y%m%d')
E = '\r\n'  # arquivos da VM usam CRLF


def backup(path):
    bak = path + f'.bak_{TODAY}'
    if os.path.exists(bak):
        print(f'[backup ok] {bak} (já existe)')
        return
    shutil.copy2(path, bak)
    print(f'[backup] {bak}')


def patch(path, old, new, desc, guard=None):
    abspath = os.path.join(BASE, path)
    with open(abspath, 'r', encoding='utf-8', newline='') as f:
        s = f.read()
    if guard and guard in s:
        print(f'[skip] {desc} (já aplicado)')
        return
    # Tolerância a EOL: arquivos da VM têm mistura CRLF/LF.
    for eol in ('\r\n', '\n'):
        old_c = old.replace('\r\n', eol)
        new_c = new.replace('\r\n', eol)
        n = s.count(old_c)
        if n == 1:
            s = s.replace(old_c, new_c, 1)
            with open(abspath, 'w', encoding='utf-8', newline='') as f:
                f.write(s)
            print(f'[ok] {desc}')
            return
    print(f'[ERRO] {path}: padrão aparece 0x (ou ambíguo) — {desc}')
    sys.exit(1)


# ---- 0. Módulo novo (enviado via scp) -------------------------------------
mod = os.path.join(BASE, 'meigestao_app/core/utils/csv_modelos.py')
if not os.path.exists(mod):
    print('[ERRO] csv_modelos.py não existe na VM — rode o scp antes.')
    sys.exit(1)
print('[ok] csv_modelos.py presente')

# ---- 1. clientes/views.py: import -----------------------------------------
backup(os.path.join(BASE, 'meigestao_app/clientes/views.py'))
patch(
    'meigestao_app/clientes/views.py',
    'from meigestao_app.core.utils.csv_importer import CSVImportService' + E,
    'from meigestao_app.core.utils.csv_importer import CSVImportService' + E
    + 'from meigestao_app.core.utils.csv_modelos import modelo_clientes_csv' + E,
    'clientes/views.py: import modelo_clientes_csv',
    guard='csv_modelos',
)

# ---- 2. clientes/urls.py: rota --------------------------------------------
backup(os.path.join(BASE, 'meigestao_app/clientes/urls.py'))
patch(
    'meigestao_app/clientes/urls.py',
    "    path('importar/', views.ClienteImportView.as_view(), name='cliente_import')," + E,
    "    path('importar/', views.ClienteImportView.as_view(), name='cliente_import')," + E
    + "    path('importar/modelo/', views.modelo_clientes_csv, name='modelo_csv')," + E,
    'clientes/urls.py: rota modelo_csv',
    guard='modelo_csv',
)

# ---- 3. estoque/views.py: import + 2 bug fixes ----------------------------
backup(os.path.join(BASE, 'meigestao_app/estoque/views.py'))
patch(
    'meigestao_app/estoque/views.py',
    'from meigestao_app.core.utils.helpers import get_empresa_do_usuario' + E,
    'from meigestao_app.core.utils.helpers import get_empresa_do_usuario' + E
    + 'from meigestao_app.core.utils.csv_modelos import modelo_produtos_csv' + E,
    'estoque/views.py: import modelo_produtos_csv',
    guard='csv_modelos',
)

# Bug fix 1: movimentação com empresa + deixar o modelo aplicar o saldo
bloco_old_1 = E.join([
    '                # 4. Inicializar Estoque',
    "                qtd_inicial_str = row.get('estoque_inicial', '0')",
    "                qtd_inicial = int(float(qtd_inicial_str.replace(',', '.'))) if qtd_inicial_str else 0",
    '                ',
    '                estoque, _ = Estoque.objects.get_or_create(produto=produto)',
    '                if qtd_inicial > 0:',
    '                    estoque.quantidade = qtd_inicial',
    '                    estoque.save()',
    '                    ',
    '                    # Registrar movimentação inicial se houver estoque',
    '                    MovimentacaoEstoque.objects.create(',
    '                        produto=produto,',
    "                        tipo_movimento='entrada',",
    '                        quantidade=qtd_inicial,',
    "                        motivo='Importação Inicial CSV'",
    '                    )',
    '',
    '                return True, ""',
]) + E
bloco_new_1 = E.join([
    '                # 4. Inicializar Estoque (via movimentação — o modelo aplica o efeito',
    '                # no estoque e valida a empresa; setar quantidade manualmente aqui',
    '                # duplicaria a contagem, pois MovimentacaoEstoque.save() soma sozinho).',
    "                qtd_inicial_str = row.get('estoque_inicial', '0')",
    "                qtd_inicial = int(float(qtd_inicial_str.replace(',', '.'))) if qtd_inicial_str else 0",
    '',
    '                if qtd_inicial > 0:',
    '                    MovimentacaoEstoque.objects.create(',
    '                        empresa=empresa,',
    '                        produto=produto,',
    "                        tipo_movimento='entrada',",
    '                        quantidade=qtd_inicial,',
    "                        motivo='Importação Inicial CSV'",
    '                    )',
    '                else:',
    '                    # Garante o registro de estoque zerado para o produto',
    "                    Estoque.objects.get_or_create(produto=produto, defaults={'empresa': empresa})",
    '',
    '                return True, ""',
]) + E
patch(
    'meigestao_app/estoque/views.py',
    bloco_old_1,
    bloco_new_1,
    'estoque/views.py: fix movimentação inicial (empresa + sem dupla contagem)',
    guard='duplicaria a contagem',
)

# Bug fix 2: categoria vazia -> 'Geral'
patch(
    'meigestao_app/estoque/views.py',
    "                cat_nome = row.get('categoria', 'Geral')" + E,
    "                cat_nome = row.get('categoria') or 'Geral'" + E,
    'estoque/views.py: fix categoria vazia → Geral',
    guard="or 'Geral'",
)

# ---- 4. estoque/urls.py: rota ---------------------------------------------
backup(os.path.join(BASE, 'meigestao_app/estoque/urls.py'))
patch(
    'meigestao_app/estoque/urls.py',
    "    path('produtos/importar/', views.ProdutoImportView.as_view(), name='produto_import')," + E,
    "    path('produtos/importar/', views.ProdutoImportView.as_view(), name='produto_import')," + E
    + "    path('produtos/importar/modelo/', views.modelo_produtos_csv, name='modelo_csv')," + E,
    'estoque/urls.py: rota modelo_csv',
    guard='modelo_csv',
)

# ---- 5. templates: botão "Baixar modelo CSV" ------------------------------
backup(os.path.join(BASE, 'templates/meigestao_app/clientes/cliente_list.html'))
tpl_cli_old = E.join([
    '                    <div class="alert alert-info border-0 rounded-4 mb-4 small">',
    '                        <i class="bi bi-info-circle-fill me-2"></i>',
    '                        O arquivo deve conter as colunas: <strong>nome</strong>, <strong>cpf_cnpj</strong>, <strong>email</strong>, <strong>telefone</strong>. ',
    '                        As colunas separadas por ponto e vírgula (;) ou vírgula (,).',
    '                    </div>',
    '                    ',
    '                    <div class="mb-4">',
]) + E
tpl_cli_new = E.join([
    '                    <div class="alert alert-info border-0 rounded-4 mb-4 small">',
    '                        <i class="bi bi-info-circle-fill me-2"></i>',
    '                        Colunas Obrigatórias: <strong>nome</strong>, <strong>cpf_cnpj</strong>.<br>',
    '                        Opcionais: <strong>email</strong>, <strong>telefone</strong>, <strong>endereco</strong>, <strong>cidade</strong>, <strong>estado</strong>, <strong>cep</strong>.<br>',
    '                        Separador: ponto e vírgula (;) ou vírgula (,).',
    '                    </div>',
    '                    ',
    '                    <div class="mb-3">',
    '                        <a href="{% url \'clientes:modelo_csv\' %}" class="btn btn-sm btn-outline-primary rounded-3">',
    '                            <i class="bi bi-download me-1"></i> Baixar modelo CSV',
    '                        </a>',
    '                        <div class="form-text">Abra o modelo no Excel, substitua a linha <strong>EXEMPLO -</strong> pelos seus dados (ou apague-a) e salve como CSV.</div>',
    '                    </div>',
    '                    ',
    '                    <div class="mb-4">',
]) + E
patch(
    'templates/meigestao_app/clientes/cliente_list.html',
    tpl_cli_old,
    tpl_cli_new,
    'cliente_list.html: botão baixar modelo CSV',
    guard='Baixar modelo CSV',
)

backup(os.path.join(BASE, 'templates/meigestao_app/estoque/produto_list.html'))
tpl_pro_old = E.join([
    '                    <div class="mb-4">',
    '                        <label for="csv_file" class="form-label fw-bold small text-secondary">Selecione o arquivo .csv</label>',
]) + E
tpl_pro_new = E.join([
    '                    <div class="mb-3">',
    '                        <a href="{% url \'estoque:modelo_csv\' %}" class="btn btn-sm btn-outline-primary rounded-3">',
    '                            <i class="bi bi-download me-1"></i> Baixar modelo CSV',
    '                        </a>',
    '                        <div class="form-text">Abra o modelo no Excel, substitua a linha <strong>EXEMPLO -</strong> pelos seus dados (ou apague-a) e salve como CSV.</div>',
    '                    </div>',
    '                    ',
    '                    <div class="mb-4">',
    '                        <label for="csv_file" class="form-label fw-bold small text-secondary">Selecione o arquivo .csv</label>',
]) + E
patch(
    'templates/meigestao_app/estoque/produto_list.html',
    tpl_pro_old,
    tpl_pro_new,
    'produto_list.html: botão baixar modelo CSV',
    guard='Baixar modelo CSV',
)

print('=== FIM: todos os patches aplicados ===')