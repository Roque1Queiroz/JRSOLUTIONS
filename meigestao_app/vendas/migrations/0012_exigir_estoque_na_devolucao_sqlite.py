from importlib import import_module

from django.db import migrations


_migracao_origem = import_module(
    'meigestao_app.vendas.migrations.0008_proteger_devolucao_estoque'
)
_SQLITE_TRIGGER_ANTERIOR = _migracao_origem.SQLITE_TRIGGERS[
    'vendas_validar_devolucao_vinculada_insert'
]
_MARCADOR = """            NEW.item_venda_id IS NOT NULL
            OR NEW.tipo_movimento <> 'devolucao'
"""
_SUBSTITUICAO = """            NEW.item_venda_id IS NOT NULL
            OR NEW.tipo_movimento <> 'devolucao'
            OR NOT EXISTS (
                SELECT 1 FROM estoque_estoque
                WHERE produto_id = NEW.produto_id
            )
"""

if _SQLITE_TRIGGER_ANTERIOR.count(_MARCADOR) != 1:
    raise RuntimeError('Estrutura inesperada do trigger SQLite de devolução.')

SQLITE_TRIGGER = _SQLITE_TRIGGER_ANTERIOR.replace(
    _MARCADOR,
    _SUBSTITUICAO,
    1,
)


def exigir_estoque_sqlite(apps, schema_editor):
    if schema_editor.connection.vendor != 'sqlite':
        return
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            'DROP TRIGGER IF EXISTS vendas_validar_devolucao_vinculada_insert'
        )
        cursor.execute(SQLITE_TRIGGER)


def restaurar_trigger_anterior(apps, schema_editor):
    if schema_editor.connection.vendor != 'sqlite':
        return
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            'DROP TRIGGER IF EXISTS vendas_validar_devolucao_vinculada_insert'
        )
        cursor.execute(_SQLITE_TRIGGER_ANTERIOR)


class Migration(migrations.Migration):
    dependencies = [
        ('vendas', '0011_bloquear_transacao_em_venda_cancelada'),
    ]

    operations = [
        migrations.RunPython(
            exigir_estoque_sqlite,
            restaurar_trigger_anterior,
        ),
    ]
