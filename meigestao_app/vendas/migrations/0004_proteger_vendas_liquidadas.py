from django.db import migrations


SQLITE_TRIGGERS = {
    'vendas_bloquear_update_liquidada': '''
        CREATE TRIGGER vendas_bloquear_update_liquidada
        BEFORE UPDATE ON vendas_venda
        FOR EACH ROW
        WHEN EXISTS (
            SELECT 1 FROM financeiro_transacao
            WHERE venda_id = OLD.id AND paga = 1
        )
        BEGIN
            SELECT RAISE(ABORT, 'Venda liquidada: estorne a transacao antes de alterar.');
        END;
    ''',
    'vendas_bloquear_delete_liquidada': '''
        CREATE TRIGGER vendas_bloquear_delete_liquidada
        BEFORE DELETE ON vendas_venda
        FOR EACH ROW
        WHEN EXISTS (
            SELECT 1 FROM financeiro_transacao
            WHERE venda_id = OLD.id AND paga = 1
        )
        BEGIN
            SELECT RAISE(ABORT, 'Venda liquidada: estorne a transacao antes de excluir.');
        END;
    ''',
    'vendas_bloquear_item_insert_liquidada': '''
        CREATE TRIGGER vendas_bloquear_item_insert_liquidada
        BEFORE INSERT ON vendas_itemvenda
        FOR EACH ROW
        WHEN EXISTS (
            SELECT 1 FROM financeiro_transacao
            WHERE venda_id = NEW.venda_id AND paga = 1
        )
        BEGIN
            SELECT RAISE(ABORT, 'Venda liquidada: estorne a transacao antes de adicionar item.');
        END;
    ''',
    'vendas_bloquear_item_update_liquidada': '''
        CREATE TRIGGER vendas_bloquear_item_update_liquidada
        BEFORE UPDATE ON vendas_itemvenda
        FOR EACH ROW
        WHEN EXISTS (
            SELECT 1 FROM financeiro_transacao
            WHERE venda_id IN (OLD.venda_id, NEW.venda_id) AND paga = 1
        )
        BEGIN
            SELECT RAISE(ABORT, 'Venda liquidada: estorne a transacao antes de alterar item.');
        END;
    ''',
    'vendas_bloquear_item_delete_liquidada': '''
        CREATE TRIGGER vendas_bloquear_item_delete_liquidada
        BEFORE DELETE ON vendas_itemvenda
        FOR EACH ROW
        WHEN EXISTS (
            SELECT 1 FROM financeiro_transacao
            WHERE venda_id = OLD.venda_id AND paga = 1
        )
        BEGIN
            SELECT RAISE(ABORT, 'Venda liquidada: estorne a transacao antes de excluir item.');
        END;
    ''',
    'vendas_bloquear_desvinculacao_transacao': '''
        CREATE TRIGGER vendas_bloquear_desvinculacao_transacao
        BEFORE UPDATE OF venda_id ON financeiro_transacao
        FOR EACH ROW
        WHEN OLD.venda_id IS NOT NULL AND NEW.venda_id IS NOT OLD.venda_id
        BEGIN
            SELECT RAISE(ABORT, 'O vinculo entre transacao e venda e imutavel.');
        END;
    ''',
    'vendas_validar_transacao_origem': '''
        CREATE TRIGGER vendas_validar_transacao_origem
        BEFORE UPDATE ON financeiro_transacao
        FOR EACH ROW
        WHEN NEW.venda_id IS NOT NULL AND (
            OLD.venda_id IS NOT NEW.venda_id
            OR NEW.empresa_id IS NOT (
                SELECT empresa_id FROM vendas_venda WHERE id = NEW.venda_id
            )
            OR NEW.tipo <> 'receita'
            OR NEW.categoria <> 'Vendas'
            OR NEW.descricao IS NOT (
                SELECT 'Venda #' || v.id || ' - ' || c.nome
                FROM vendas_venda v
                JOIN clientes_cliente c ON c.id = v.cliente_id
                WHERE v.id = NEW.venda_id
            )
            OR NEW.valor IS NOT (
                SELECT valor_total FROM vendas_venda WHERE id = NEW.venda_id
            )
        )
        BEGIN
            SELECT RAISE(ABORT, 'Transacao de venda deve refletir os dados da venda.');
        END;
    ''',
    'vendas_validar_transacao_origem_insert': '''
        CREATE TRIGGER vendas_validar_transacao_origem_insert
        BEFORE INSERT ON financeiro_transacao
        FOR EACH ROW
        WHEN NEW.venda_id IS NOT NULL AND (
            NEW.paga = 1
            OR NEW.empresa_id IS NOT (
                SELECT empresa_id FROM vendas_venda WHERE id = NEW.venda_id
            )
            OR NEW.tipo <> 'receita'
            OR NEW.categoria <> 'Vendas'
            OR NEW.descricao IS NOT (
                SELECT 'Venda #' || v.id || ' - ' || c.nome
                FROM vendas_venda v
                JOIN clientes_cliente c ON c.id = v.cliente_id
                WHERE v.id = NEW.venda_id
            )
            OR NEW.valor IS NOT (
                SELECT valor_total FROM vendas_venda WHERE id = NEW.venda_id
            )
        )
        BEGIN
            SELECT RAISE(ABORT, 'Transacao de venda deve nascer pendente e refletir a venda.');
        END;
    ''',
    'vendas_aplicar_saldo_transacao': '''
        CREATE TRIGGER vendas_aplicar_saldo_transacao
        AFTER UPDATE ON financeiro_transacao
        FOR EACH ROW
        WHEN NEW.venda_id IS NOT NULL
             AND NEW.paga = 1
             AND NEW.conta_id IS NOT NULL
             AND (OLD.paga = 0 OR OLD.conta_id IS NOT NEW.conta_id)
        BEGIN
            UPDATE financeiro_contabancaria
            SET saldo = saldo + NEW.valor
            WHERE id = NEW.conta_id;
        END;
    ''',
    'vendas_reverter_saldo_transacao': '''
        CREATE TRIGGER vendas_reverter_saldo_transacao
        AFTER UPDATE ON financeiro_transacao
        FOR EACH ROW
        WHEN OLD.venda_id IS NOT NULL
             AND OLD.paga = 1
             AND OLD.conta_id IS NOT NULL
             AND (NEW.paga = 0 OR NEW.conta_id IS NOT OLD.conta_id)
        BEGIN
            UPDATE financeiro_contabancaria
            SET saldo = saldo - OLD.valor
            WHERE id = OLD.conta_id;
        END;
    ''',
    'vendas_bloquear_transacao_paga_delete': '''
        CREATE TRIGGER vendas_bloquear_transacao_paga_delete
        BEFORE DELETE ON financeiro_transacao
        FOR EACH ROW
        WHEN OLD.venda_id IS NOT NULL AND OLD.paga = 1
        BEGIN
            SELECT RAISE(ABORT, 'Transacao paga de venda deve ser estornada antes da exclusao.');
        END;
    ''',
}


POSTGRES_FUNCTION = '''
CREATE OR REPLACE FUNCTION vendas_proteger_liquidacao()
RETURNS trigger AS $$
DECLARE
    venda_alvo bigint;
BEGIN
    IF TG_TABLE_NAME = 'vendas_venda' THEN
        venda_alvo := OLD.id;
    ELSIF TG_OP = 'INSERT' THEN
        venda_alvo := NEW.venda_id;
    ELSE
        venda_alvo := OLD.venda_id;
    END IF;

    PERFORM id FROM vendas_venda WHERE id = venda_alvo FOR UPDATE;

    IF TG_TABLE_NAME = 'vendas_itemvenda' AND TG_OP = 'UPDATE'
       AND NEW.venda_id <> OLD.venda_id THEN
        PERFORM id FROM vendas_venda WHERE id = NEW.venda_id FOR UPDATE;
        IF EXISTS (
            SELECT 1 FROM financeiro_transacao
            WHERE venda_id = NEW.venda_id AND paga
        ) THEN
            RAISE EXCEPTION 'Venda liquidada: estorne a transacao antes de mover item.';
        END IF;
    END IF;

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

POSTGRES_TRIGGERS = [
    '''CREATE TRIGGER vendas_bloquear_update_delete_liquidada
       BEFORE UPDATE OR DELETE ON vendas_venda
       FOR EACH ROW EXECUTE FUNCTION vendas_proteger_liquidacao();''',
    '''CREATE TRIGGER vendas_bloquear_item_liquidada
       BEFORE INSERT OR UPDATE OR DELETE ON vendas_itemvenda
       FOR EACH ROW EXECUTE FUNCTION vendas_proteger_liquidacao();''',
]

POSTGRES_FINANCE_FUNCTION = '''
CREATE OR REPLACE FUNCTION vendas_validar_transacao_origem()
RETURNS trigger AS $$
DECLARE
    venda_atual vendas_venda%ROWTYPE;
    cliente_nome varchar;
    venda_alvo bigint;
BEGIN
    IF TG_OP = 'UPDATE'
       AND OLD.venda_id IS NOT NULL
       AND NEW.venda_id IS DISTINCT FROM OLD.venda_id THEN
        RAISE EXCEPTION 'O vinculo entre transacao e venda e imutavel.';
    END IF;

    IF TG_OP = 'DELETE' THEN
        venda_alvo := OLD.venda_id;
    ELSE
        venda_alvo := NEW.venda_id;
    END IF;

    IF venda_alvo IS NULL THEN
        IF TG_OP = 'DELETE' THEN
            RETURN OLD;
        END IF;
        RETURN NEW;
    END IF;

    SELECT * INTO venda_atual
    FROM vendas_venda
    WHERE id = venda_alvo
    FOR UPDATE;

    IF TG_OP = 'DELETE' THEN
        IF OLD.paga THEN
            RAISE EXCEPTION 'Transacao paga de venda deve ser estornada antes da exclusao.';
        END IF;
        RETURN OLD;
    END IF;

    SELECT nome INTO cliente_nome
    FROM clientes_cliente
    WHERE id = venda_atual.cliente_id;

    IF (TG_OP = 'INSERT' AND NEW.paga)
       OR (TG_OP = 'UPDATE' AND NEW.venda_id IS DISTINCT FROM OLD.venda_id)
       OR NEW.empresa_id IS DISTINCT FROM venda_atual.empresa_id
       OR NEW.tipo IS DISTINCT FROM 'receita'
       OR NEW.categoria IS DISTINCT FROM 'Vendas'
       OR NEW.descricao IS DISTINCT FROM
          ('Venda #' || venda_atual.id || ' - ' || cliente_nome)
       OR NEW.valor IS DISTINCT FROM venda_atual.valor_total THEN
        RAISE EXCEPTION 'Transacao de venda deve nascer pendente e refletir os dados da venda.';
    END IF;

    IF TG_OP = 'UPDATE' THEN
        PERFORM id
        FROM financeiro_contabancaria
        WHERE id IN (OLD.conta_id, NEW.conta_id)
        ORDER BY id
        FOR UPDATE;

        IF OLD.paga AND OLD.conta_id IS NOT NULL
           AND (NOT NEW.paga OR NEW.conta_id IS DISTINCT FROM OLD.conta_id) THEN
            UPDATE financeiro_contabancaria
            SET saldo = saldo - OLD.valor
            WHERE id = OLD.conta_id;
        END IF;

        IF NEW.paga AND NEW.conta_id IS NOT NULL
           AND (NOT OLD.paga OR NEW.conta_id IS DISTINCT FROM OLD.conta_id) THEN
            UPDATE financeiro_contabancaria
            SET saldo = saldo + NEW.valor
            WHERE id = NEW.conta_id;
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
'''

POSTGRES_FINANCE_TRIGGER = '''
CREATE TRIGGER vendas_validar_transacao_origem
BEFORE INSERT OR UPDATE OR DELETE ON financeiro_transacao
FOR EACH ROW EXECUTE FUNCTION vendas_validar_transacao_origem();
'''


def criar_triggers(apps, schema_editor):
    vendor = schema_editor.connection.vendor
    with schema_editor.connection.cursor() as cursor:
        if vendor == 'sqlite':
            for sql in SQLITE_TRIGGERS.values():
                cursor.execute(sql)
        elif vendor == 'postgresql':
            cursor.execute(POSTGRES_FUNCTION)
            for sql in POSTGRES_TRIGGERS:
                cursor.execute(sql)
            cursor.execute(POSTGRES_FINANCE_FUNCTION)
            cursor.execute(POSTGRES_FINANCE_TRIGGER)


def remover_triggers(apps, schema_editor):
    vendor = schema_editor.connection.vendor
    with schema_editor.connection.cursor() as cursor:
        if vendor == 'sqlite':
            for nome in SQLITE_TRIGGERS:
                cursor.execute(f'DROP TRIGGER IF EXISTS {nome}')
        elif vendor == 'postgresql':
            cursor.execute(
                'DROP TRIGGER IF EXISTS vendas_bloquear_update_delete_liquidada '
                'ON vendas_venda'
            )
            cursor.execute(
                'DROP TRIGGER IF EXISTS vendas_bloquear_item_liquidada '
                'ON vendas_itemvenda'
            )
            cursor.execute(
                'DROP TRIGGER IF EXISTS vendas_validar_transacao_origem '
                'ON financeiro_transacao'
            )
            cursor.execute('DROP FUNCTION IF EXISTS vendas_proteger_liquidacao()')
            cursor.execute('DROP FUNCTION IF EXISTS vendas_validar_transacao_origem()')


class Migration(migrations.Migration):

    dependencies = [
        ('financeiro', '0007_reciboreembolso_prioridade'),
        ('vendas', '0003_remove_itemvenda_produto_itemvenda_produto_nome_and_more'),
    ]

    operations = [
        migrations.RunPython(criar_triggers, remover_triggers),
    ]
