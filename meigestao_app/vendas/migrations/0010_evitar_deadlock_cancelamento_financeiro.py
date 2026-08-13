from importlib import import_module

from django.db import migrations


_migracao_origem = import_module(
    'meigestao_app.vendas.migrations.0004_proteger_vendas_liquidadas'
)
_POSTGRES_FUNCTION_ANTERIOR = _migracao_origem.POSTGRES_FINANCE_FUNCTION
_MARCADOR = """    WHERE id = venda_alvo
    FOR UPDATE;
"""
_SUBSTITUICAO = """    WHERE id = venda_alvo
    FOR UPDATE NOWAIT;
"""

if _POSTGRES_FUNCTION_ANTERIOR.count(_MARCADOR) != 1:
    raise RuntimeError('Estrutura inesperada da função financeira de vendas.')

POSTGRES_FUNCTION = _POSTGRES_FUNCTION_ANTERIOR.replace(
    _MARCADOR,
    _SUBSTITUICAO,
    1,
)


def corrigir_lock_financeiro(apps, schema_editor):
    if schema_editor.connection.vendor != 'postgresql':
        return
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(POSTGRES_FUNCTION)


def restaurar_funcao_anterior(apps, schema_editor):
    if schema_editor.connection.vendor != 'postgresql':
        return
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(_POSTGRES_FUNCTION_ANTERIOR)


class Migration(migrations.Migration):
    dependencies = [
        ('vendas', '0009_corrigir_insert_devolucao_postgresql'),
    ]

    operations = [
        migrations.RunPython(
            corrigir_lock_financeiro,
            restaurar_funcao_anterior,
        ),
    ]
