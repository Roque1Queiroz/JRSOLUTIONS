from importlib import import_module

from django.db import migrations


_migracao_origem = import_module(
    'meigestao_app.vendas.migrations.0004_proteger_vendas_liquidadas'
)
_migracao_nowait = import_module(
    'meigestao_app.vendas.migrations.0010_evitar_deadlock_cancelamento_financeiro'
)

_SQLITE_INSERT_ANTERIOR = _migracao_origem.SQLITE_TRIGGERS[
    'vendas_validar_transacao_origem_insert'
]
_SQLITE_UPDATE_ANTERIOR = _migracao_origem.SQLITE_TRIGGERS[
    'vendas_validar_transacao_origem'
]

_SQLITE_INSERT_MARCADOR = """WHEN NEW.venda_id IS NOT NULL AND (
            NEW.paga = 1
"""
_SQLITE_INSERT_SUBSTITUICAO = """WHEN NEW.venda_id IS NOT NULL AND (
            (SELECT status FROM vendas_venda WHERE id = NEW.venda_id) = 'cancelada'
            OR NEW.paga = 1
"""
_SQLITE_UPDATE_MARCADOR = """WHEN NEW.venda_id IS NOT NULL AND (
            OLD.venda_id IS NOT NEW.venda_id
"""
_SQLITE_UPDATE_SUBSTITUICAO = """WHEN NEW.venda_id IS NOT NULL AND (
            (SELECT status FROM vendas_venda WHERE id = NEW.venda_id) = 'cancelada'
            OR OLD.venda_id IS NOT NEW.venda_id
"""

if _SQLITE_INSERT_ANTERIOR.count(_SQLITE_INSERT_MARCADOR) != 1:
    raise RuntimeError('Estrutura inesperada do trigger SQLite de INSERT financeiro.')
if _SQLITE_UPDATE_ANTERIOR.count(_SQLITE_UPDATE_MARCADOR) != 1:
    raise RuntimeError('Estrutura inesperada do trigger SQLite de UPDATE financeiro.')

SQLITE_INSERT = _SQLITE_INSERT_ANTERIOR.replace(
    _SQLITE_INSERT_MARCADOR,
    _SQLITE_INSERT_SUBSTITUICAO,
    1,
)
SQLITE_UPDATE = _SQLITE_UPDATE_ANTERIOR.replace(
    _SQLITE_UPDATE_MARCADOR,
    _SQLITE_UPDATE_SUBSTITUICAO,
    1,
)

_POSTGRES_FUNCTION_ANTERIOR = _migracao_nowait.POSTGRES_FUNCTION
_POSTGRES_MARCADOR = """    IF TG_OP = 'DELETE' THEN
        IF OLD.paga THEN
            RAISE EXCEPTION 'Transacao paga de venda deve ser estornada antes da exclusao.';
        END IF;
        RETURN OLD;
    END IF;

    SELECT nome INTO cliente_nome
"""
_POSTGRES_SUBSTITUICAO = """    IF TG_OP = 'DELETE' THEN
        IF OLD.paga THEN
            RAISE EXCEPTION 'Transacao paga de venda deve ser estornada antes da exclusao.';
        END IF;
        RETURN OLD;
    END IF;

    IF venda_atual.status = 'cancelada' THEN
        RAISE EXCEPTION 'Venda cancelada nao pode possuir transacao financeira.';
    END IF;

    SELECT nome INTO cliente_nome
"""

if _POSTGRES_FUNCTION_ANTERIOR.count(_POSTGRES_MARCADOR) != 1:
    raise RuntimeError('Estrutura inesperada da função PostgreSQL financeira.')

POSTGRES_FUNCTION = _POSTGRES_FUNCTION_ANTERIOR.replace(
    _POSTGRES_MARCADOR,
    _POSTGRES_SUBSTITUICAO,
    1,
)


def proteger_venda_cancelada(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        if schema_editor.connection.vendor == 'sqlite':
            cursor.execute('DROP TRIGGER IF EXISTS vendas_validar_transacao_origem')
            cursor.execute(
                'DROP TRIGGER IF EXISTS vendas_validar_transacao_origem_insert'
            )
            cursor.execute(SQLITE_UPDATE)
            cursor.execute(SQLITE_INSERT)
        elif schema_editor.connection.vendor == 'postgresql':
            cursor.execute(POSTGRES_FUNCTION)


def restaurar_protecao_anterior(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        if schema_editor.connection.vendor == 'sqlite':
            cursor.execute('DROP TRIGGER IF EXISTS vendas_validar_transacao_origem')
            cursor.execute(
                'DROP TRIGGER IF EXISTS vendas_validar_transacao_origem_insert'
            )
            cursor.execute(_SQLITE_UPDATE_ANTERIOR)
            cursor.execute(_SQLITE_INSERT_ANTERIOR)
        elif schema_editor.connection.vendor == 'postgresql':
            cursor.execute(_POSTGRES_FUNCTION_ANTERIOR)


class Migration(migrations.Migration):
    dependencies = [
        ('vendas', '0010_evitar_deadlock_cancelamento_financeiro'),
    ]

    operations = [
        migrations.RunPython(
            proteger_venda_cancelada,
            restaurar_protecao_anterior,
        ),
    ]
