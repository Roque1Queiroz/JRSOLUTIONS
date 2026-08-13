from django.db import migrations


SQLITE_TRIGGERS = {
    'vendas_bloquear_item_controlado_insert_ativa': '''
        CREATE TRIGGER vendas_bloquear_item_controlado_insert_ativa
        BEFORE INSERT ON vendas_itemvenda
        FOR EACH ROW
        WHEN NEW.produto_vinculado_id IS NOT NULL
             AND EXISTS (
                 SELECT 1 FROM vendas_venda venda
                 WHERE venda.id = NEW.venda_id
                   AND venda.status IN ('confirmada', 'entregue')
             )
        BEGIN
            SELECT RAISE(ABORT, 'Produto controlado deve ser adicionado antes da confirmacao.');
        END;
    ''',
    'vendas_exigir_baixa_estoque_antes_confirmacao': '''
        CREATE TRIGGER vendas_exigir_baixa_estoque_antes_confirmacao
        BEFORE UPDATE OF status ON vendas_venda
        FOR EACH ROW
        WHEN NEW.status IN ('confirmada', 'entregue')
             AND OLD.status NOT IN ('confirmada', 'entregue')
             AND EXISTS (
                 SELECT 1
                 FROM vendas_itemvenda item
                 WHERE item.venda_id = NEW.id
                   AND item.produto_vinculado_id IS NOT NULL
                   AND NOT EXISTS (
                       SELECT 1
                       FROM estoque_movimentacaoestoque movimento
                       WHERE movimento.item_venda_id = item.id
                         AND movimento.produto_id = item.produto_vinculado_id
                         AND movimento.tipo_movimento = 'saida'
                         AND movimento.quantidade = item.quantidade
                   )
             )
        BEGIN
            SELECT RAISE(ABORT, 'Confirme a venda pelo servico de baixa de estoque.');
        END;
    ''',
    'vendas_bloquear_item_com_baixa_update': '''
        CREATE TRIGGER vendas_bloquear_item_com_baixa_update
        BEFORE UPDATE ON vendas_itemvenda
        FOR EACH ROW
        WHEN (
            NEW.produto_vinculado_id IS NOT NULL
            AND EXISTS (
                SELECT 1 FROM vendas_venda venda
                WHERE venda.id = NEW.venda_id
                  AND venda.status IN ('confirmada', 'entregue')
            )
            AND NOT EXISTS (
                SELECT 1 FROM estoque_movimentacaoestoque movimento
                WHERE movimento.item_venda_id = OLD.id
                  AND movimento.produto_id = NEW.produto_vinculado_id
                  AND movimento.tipo_movimento = 'saida'
                  AND movimento.quantidade = NEW.quantidade
            )
        ) OR (
            EXISTS (
                SELECT 1 FROM estoque_movimentacaoestoque movimento
                WHERE movimento.item_venda_id = OLD.id
            ) AND (
                NEW.venda_id IS NOT OLD.venda_id
                OR NEW.produto_vinculado_id IS NOT OLD.produto_vinculado_id
                OR NEW.quantidade IS NOT OLD.quantidade
            )
        )
        BEGIN
            SELECT RAISE(ABORT, 'Item com baixa de estoque e imutavel.');
        END;
    ''',
    'vendas_validar_movimento_vinculado_insert': '''
        CREATE TRIGGER vendas_validar_movimento_vinculado_insert
        BEFORE INSERT ON estoque_movimentacaoestoque
        FOR EACH ROW
        WHEN NEW.item_venda_id IS NOT NULL AND (
            NEW.tipo_movimento <> 'saida'
            OR NEW.produto_id IS NOT (
                SELECT produto_vinculado_id FROM vendas_itemvenda
                WHERE id = NEW.item_venda_id
            )
            OR NEW.quantidade IS NOT (
                SELECT quantidade FROM vendas_itemvenda
                WHERE id = NEW.item_venda_id
            )
            OR NEW.empresa_id IS NOT (
                SELECT venda.empresa_id
                FROM vendas_itemvenda item
                JOIN vendas_venda venda ON venda.id = item.venda_id
                WHERE item.id = NEW.item_venda_id
            )
            OR COALESCE((
                SELECT quantidade FROM estoque_estoque
                WHERE produto_id = NEW.produto_id
            ), 0) < NEW.quantidade
        )
        BEGIN
            SELECT RAISE(ABORT, 'Movimento vinculado invalido ou estoque insuficiente.');
        END;
    ''',
    'vendas_aplicar_movimento_vinculado_insert': '''
        CREATE TRIGGER vendas_aplicar_movimento_vinculado_insert
        AFTER INSERT ON estoque_movimentacaoestoque
        FOR EACH ROW
        WHEN NEW.item_venda_id IS NOT NULL
        BEGIN
            UPDATE estoque_estoque
            SET quantidade = quantidade - NEW.quantidade
            WHERE produto_id = NEW.produto_id;
        END;
    ''',
    'vendas_bloquear_movimento_vinculado_update': '''
        CREATE TRIGGER vendas_bloquear_movimento_vinculado_update
        BEFORE UPDATE ON estoque_movimentacaoestoque
        FOR EACH ROW
        WHEN NEW.item_venda_id IS NOT OLD.item_venda_id
             OR (
                OLD.item_venda_id IS NOT NULL AND (
                    NEW.empresa_id IS NOT OLD.empresa_id
                    OR NEW.produto_id IS NOT OLD.produto_id
                    OR NEW.tipo_movimento IS NOT OLD.tipo_movimento
                    OR NEW.quantidade IS NOT OLD.quantidade
                )
             )
        BEGIN
            SELECT RAISE(ABORT, 'Movimento de venda e imutavel.');
        END;
    ''',
    'vendas_bloquear_movimento_vinculado_delete': '''
        CREATE TRIGGER vendas_bloquear_movimento_vinculado_delete
        BEFORE DELETE ON estoque_movimentacaoestoque
        FOR EACH ROW
        WHEN OLD.item_venda_id IS NOT NULL
        BEGIN
            SELECT RAISE(ABORT, 'Movimento de venda nao pode ser excluido.');
        END;
    ''',
}

POSTGRES_FUNCTION = '''
CREATE OR REPLACE FUNCTION vendas_proteger_baixa_estoque()
RETURNS trigger AS $$
DECLARE
    estoque_atual estoque_estoque%ROWTYPE;
    item_atual vendas_itemvenda%ROWTYPE;
    venda_atual vendas_venda%ROWTYPE;
    venda_id_inicial bigint;
BEGIN
    IF TG_TABLE_NAME = 'estoque_movimentacaoestoque' THEN
        IF TG_OP = 'INSERT' AND NEW.item_venda_id IS NOT NULL THEN
            SELECT venda_id INTO venda_id_inicial
            FROM vendas_itemvenda
            WHERE id = NEW.item_venda_id;

            IF NOT FOUND THEN
                RAISE EXCEPTION 'Item da venda nao encontrado.';
            END IF;

            SELECT * INTO venda_atual
            FROM vendas_venda
            WHERE id = venda_id_inicial
            FOR UPDATE;

            SELECT * INTO item_atual
            FROM vendas_itemvenda
            WHERE id = NEW.item_venda_id
            FOR UPDATE NOWAIT;

            IF NOT FOUND
               OR item_atual.venda_id IS DISTINCT FROM venda_atual.id
               OR NEW.tipo_movimento IS DISTINCT FROM 'saida'
               OR NEW.produto_id IS DISTINCT FROM item_atual.produto_vinculado_id
               OR NEW.quantidade IS DISTINCT FROM item_atual.quantidade
               OR NEW.empresa_id IS DISTINCT FROM venda_atual.empresa_id THEN
                RAISE EXCEPTION 'Movimento vinculado nao reflete o item da venda.';
            END IF;

            SELECT * INTO estoque_atual
            FROM estoque_estoque
            WHERE produto_id = NEW.produto_id
            FOR UPDATE;

            IF NOT FOUND OR estoque_atual.quantidade < NEW.quantidade THEN
                RAISE EXCEPTION 'Estoque insuficiente para confirmar a venda.';
            END IF;

            UPDATE estoque_estoque
            SET quantidade = quantidade - NEW.quantidade
            WHERE id = estoque_atual.id;
            RETURN NEW;
        END IF;

        IF TG_OP = 'DELETE' THEN
            IF OLD.item_venda_id IS NOT NULL THEN
                RAISE EXCEPTION 'Movimento de venda nao pode ser excluido.';
            END IF;
            RETURN OLD;
        END IF;

        IF NEW.item_venda_id IS DISTINCT FROM OLD.item_venda_id
           OR (
               OLD.item_venda_id IS NOT NULL AND (
                   NEW.empresa_id IS DISTINCT FROM OLD.empresa_id
                   OR NEW.produto_id IS DISTINCT FROM OLD.produto_id
                   OR NEW.tipo_movimento IS DISTINCT FROM OLD.tipo_movimento
                   OR NEW.quantidade IS DISTINCT FROM OLD.quantidade
               )
           ) THEN
            RAISE EXCEPTION 'Movimento de venda e imutavel.';
        END IF;
        RETURN NEW;
    END IF;

    IF TG_TABLE_NAME = 'vendas_itemvenda' AND TG_OP = 'INSERT' THEN
        IF NEW.produto_vinculado_id IS NOT NULL
           AND EXISTS (
               SELECT 1 FROM vendas_venda venda
               WHERE venda.id = NEW.venda_id
                 AND venda.status IN ('confirmada', 'entregue')
           ) THEN
            RAISE EXCEPTION 'Produto controlado deve ser adicionado antes da confirmacao.';
        END IF;
        RETURN NEW;
    END IF;

    IF TG_TABLE_NAME = 'vendas_venda' THEN
        IF NEW.status IN ('confirmada', 'entregue')
           AND OLD.status NOT IN ('confirmada', 'entregue')
           AND EXISTS (
               SELECT 1
               FROM vendas_itemvenda item
               WHERE item.venda_id = NEW.id
                 AND item.produto_vinculado_id IS NOT NULL
                 AND NOT EXISTS (
                     SELECT 1
                     FROM estoque_movimentacaoestoque movimento
                     WHERE movimento.item_venda_id = item.id
                       AND movimento.produto_id = item.produto_vinculado_id
                       AND movimento.tipo_movimento = 'saida'
                       AND movimento.quantidade = item.quantidade
                 )
           ) THEN
            RAISE EXCEPTION 'Confirme a venda pelo servico de baixa de estoque.';
        END IF;
        RETURN NEW;
    END IF;

    IF TG_TABLE_NAME = 'vendas_itemvenda' THEN
        IF (
            NEW.produto_vinculado_id IS NOT NULL
            AND EXISTS (
                SELECT 1 FROM vendas_venda venda
                WHERE venda.id = NEW.venda_id
                  AND venda.status IN ('confirmada', 'entregue')
            )
            AND NOT EXISTS (
                SELECT 1 FROM estoque_movimentacaoestoque movimento
                WHERE movimento.item_venda_id = OLD.id
                  AND movimento.produto_id = NEW.produto_vinculado_id
                  AND movimento.tipo_movimento = 'saida'
                  AND movimento.quantidade = NEW.quantidade
            )
        ) OR (
            EXISTS (
                SELECT 1 FROM estoque_movimentacaoestoque movimento
                WHERE movimento.item_venda_id = OLD.id
            ) AND (
                NEW.venda_id IS DISTINCT FROM OLD.venda_id
                OR NEW.produto_vinculado_id IS DISTINCT FROM OLD.produto_vinculado_id
                OR NEW.quantidade IS DISTINCT FROM OLD.quantidade
            )
        ) THEN
            RAISE EXCEPTION 'Item com baixa de estoque e imutavel.';
        END IF;
        RETURN NEW;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
'''

POSTGRES_TRIGGERS = [
    '''CREATE TRIGGER vendas_bloquear_item_controlado_insert_ativa
       BEFORE INSERT ON vendas_itemvenda
       FOR EACH ROW EXECUTE FUNCTION vendas_proteger_baixa_estoque();''',
    '''CREATE TRIGGER vendas_exigir_baixa_estoque_antes_confirmacao
       BEFORE UPDATE OF status ON vendas_venda
       FOR EACH ROW EXECUTE FUNCTION vendas_proteger_baixa_estoque();''',
    '''CREATE TRIGGER vendas_bloquear_item_com_baixa_update
       BEFORE UPDATE ON vendas_itemvenda
       FOR EACH ROW EXECUTE FUNCTION vendas_proteger_baixa_estoque();''',
    '''CREATE TRIGGER vendas_aplicar_movimento_vinculado_insert
       BEFORE INSERT ON estoque_movimentacaoestoque
       FOR EACH ROW EXECUTE FUNCTION vendas_proteger_baixa_estoque();''',
    '''CREATE TRIGGER vendas_bloquear_movimento_vinculado
       BEFORE UPDATE OR DELETE ON estoque_movimentacaoestoque
       FOR EACH ROW EXECUTE FUNCTION vendas_proteger_baixa_estoque();''',
]


def criar_triggers(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        if schema_editor.connection.vendor == 'sqlite':
            for sql in SQLITE_TRIGGERS.values():
                cursor.execute(sql)
        elif schema_editor.connection.vendor == 'postgresql':
            cursor.execute(POSTGRES_FUNCTION)
            for sql in POSTGRES_TRIGGERS:
                cursor.execute(sql)


def remover_triggers(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        if schema_editor.connection.vendor == 'sqlite':
            for nome in SQLITE_TRIGGERS:
                cursor.execute(f'DROP TRIGGER IF EXISTS {nome}')
        elif schema_editor.connection.vendor == 'postgresql':
            cursor.execute(
                'DROP TRIGGER IF EXISTS vendas_bloquear_item_controlado_insert_ativa '
                'ON vendas_itemvenda'
            )
            cursor.execute(
                'DROP TRIGGER IF EXISTS vendas_exigir_baixa_estoque_antes_confirmacao '
                'ON vendas_venda'
            )
            cursor.execute(
                'DROP TRIGGER IF EXISTS vendas_bloquear_item_com_baixa_update '
                'ON vendas_itemvenda'
            )
            cursor.execute(
                'DROP TRIGGER IF EXISTS vendas_aplicar_movimento_vinculado_insert '
                'ON estoque_movimentacaoestoque'
            )
            cursor.execute(
                'DROP TRIGGER IF EXISTS vendas_bloquear_movimento_vinculado '
                'ON estoque_movimentacaoestoque'
            )
            cursor.execute('DROP FUNCTION IF EXISTS vendas_proteger_baixa_estoque()')


class Migration(migrations.Migration):

    dependencies = [
        ('estoque', '0004_movimentacaoestoque_item_venda'),
        ('vendas', '0004_proteger_vendas_liquidadas'),
    ]

    operations = [
        migrations.RunPython(criar_triggers, remover_triggers),
    ]
