from importlib import import_module

from django.db import migrations


_migracao_baixa = import_module(
    'meigestao_app.vendas.migrations.0005_exigir_baixa_estoque_confirmacao'
)
_POSTGRES_FUNCTION_ANTERIOR = _migracao_baixa.POSTGRES_FUNCTION
_MARCADOR = """        IF TG_OP = 'DELETE' THEN
"""
_SUBSTITUICAO = """        IF TG_OP = 'INSERT' THEN
            RETURN NEW;
        END IF;

        IF TG_OP = 'DELETE' THEN
"""

if _POSTGRES_FUNCTION_ANTERIOR.count(_MARCADOR) != 1:
    raise RuntimeError('Estrutura inesperada da função de baixa de estoque.')

POSTGRES_FUNCTION = _POSTGRES_FUNCTION_ANTERIOR.replace(
    _MARCADOR,
    _SUBSTITUICAO,
    1,
)


def corrigir_insert_devolucao(apps, schema_editor):
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
        ('vendas', '0008_proteger_devolucao_estoque'),
    ]

    operations = [
        migrations.RunPython(
            corrigir_insert_devolucao,
            restaurar_funcao_anterior,
        ),
    ]
