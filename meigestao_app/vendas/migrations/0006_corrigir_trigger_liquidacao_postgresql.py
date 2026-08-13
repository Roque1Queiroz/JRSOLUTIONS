from django.db import migrations


POSTGRES_FUNCTION = '''
CREATE OR REPLACE FUNCTION vendas_proteger_liquidacao()
RETURNS trigger AS $$
DECLARE
    venda_alvo bigint;
BEGIN
    IF TG_TABLE_NAME = 'vendas_venda' THEN
        venda_alvo := OLD.id;

    ELSIF TG_TABLE_NAME = 'vendas_itemvenda' THEN
        IF TG_OP = 'INSERT' THEN
            venda_alvo := NEW.venda_id;
        ELSE
            venda_alvo := OLD.venda_id;
        END IF;

        IF TG_OP = 'UPDATE'
           AND NEW.venda_id IS DISTINCT FROM OLD.venda_id THEN
            PERFORM id FROM vendas_venda WHERE id = NEW.venda_id FOR UPDATE;
            IF EXISTS (
                SELECT 1 FROM financeiro_transacao
                WHERE venda_id = NEW.venda_id AND paga
            ) THEN
                RAISE EXCEPTION 'Venda liquidada: estorne a transacao antes de mover item.';
            END IF;
        END IF;

    ELSE
        RAISE EXCEPTION 'Tabela inesperada no trigger de liquidacao: %', TG_TABLE_NAME;
    END IF;

    PERFORM id FROM vendas_venda WHERE id = venda_alvo FOR UPDATE;

    IF EXISTS (
        SELECT 1 FROM financeiro_transacao
        WHERE venda_id = venda_alvo AND paga
    ) THEN
        RAISE EXCEPTION 'Venda liquidada: estorne a transacao antes da mutacao.';
    END IF;

    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
'''


def corrigir_funcao(apps, schema_editor):
    if schema_editor.connection.vendor != 'postgresql':
        return
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(POSTGRES_FUNCTION)


def restaurar_funcao_anterior(apps, schema_editor):
    if schema_editor.connection.vendor != 'postgresql':
        return

    from importlib import import_module

    migracao_anterior = import_module(
        'meigestao_app.vendas.migrations.0004_proteger_vendas_liquidadas'
    )
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(migracao_anterior.POSTGRES_FUNCTION)


class Migration(migrations.Migration):
    dependencies = [
        ('vendas', '0005_exigir_baixa_estoque_confirmacao'),
    ]

    operations = [
        migrations.RunPython(corrigir_funcao, restaurar_funcao_anterior),
    ]
