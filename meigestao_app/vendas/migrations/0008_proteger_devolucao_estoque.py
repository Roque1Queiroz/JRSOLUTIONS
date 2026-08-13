from django.db import migrations


SQLITE_TRIGGERS = {
    'vendas_validar_devolucao_vinculada_insert': '''
        CREATE TRIGGER vendas_validar_devolucao_vinculada_insert
        BEFORE INSERT ON estoque_movimentacaoestoque
        FOR EACH ROW
        WHEN NEW.movimento_saida_estornado_id IS NOT NULL AND (
            NEW.item_venda_id IS NOT NULL
            OR NEW.tipo_movimento <> 'devolucao'
            OR NEW.empresa_id IS NOT (
                SELECT venda.empresa_id
                FROM estoque_movimentacaoestoque saida
                JOIN vendas_itemvenda item ON item.id = saida.item_venda_id
                JOIN vendas_venda venda ON venda.id = item.venda_id
                WHERE saida.id = NEW.movimento_saida_estornado_id
                  AND saida.tipo_movimento = 'saida'
            )
            OR NEW.produto_id IS NOT (
                SELECT produto_id FROM estoque_movimentacaoestoque
                WHERE id = NEW.movimento_saida_estornado_id
                  AND item_venda_id IS NOT NULL
                  AND tipo_movimento = 'saida'
            )
            OR NEW.quantidade IS NOT (
                SELECT quantidade FROM estoque_movimentacaoestoque
                WHERE id = NEW.movimento_saida_estornado_id
                  AND item_venda_id IS NOT NULL
                  AND tipo_movimento = 'saida'
            )
        )
        BEGIN
            SELECT RAISE(ABORT, 'Devolucao vinculada nao reflete a saida da venda.');
        END;
    ''',
    'vendas_aplicar_devolucao_vinculada_insert': '''
        CREATE TRIGGER vendas_aplicar_devolucao_vinculada_insert
        AFTER INSERT ON estoque_movimentacaoestoque
        FOR EACH ROW
        WHEN NEW.movimento_saida_estornado_id IS NOT NULL
        BEGIN
            UPDATE estoque_estoque
            SET quantidade = quantidade + NEW.quantidade
            WHERE produto_id = NEW.produto_id;
        END;
    ''',
    'vendas_bloquear_devolucao_vinculada_update': '''
        CREATE TRIGGER vendas_bloquear_devolucao_vinculada_update
        BEFORE UPDATE ON estoque_movimentacaoestoque
        FOR EACH ROW
        WHEN NEW.movimento_saida_estornado_id IS NOT OLD.movimento_saida_estornado_id
             OR (
                OLD.movimento_saida_estornado_id IS NOT NULL AND (
                    NEW.item_venda_id IS NOT OLD.item_venda_id
                    OR NEW.empresa_id IS NOT OLD.empresa_id
                    OR NEW.produto_id IS NOT OLD.produto_id
                    OR NEW.tipo_movimento IS NOT OLD.tipo_movimento
                    OR NEW.quantidade IS NOT OLD.quantidade
                )
             )
        BEGIN
            SELECT RAISE(ABORT, 'Devolucao de venda e imutavel.');
        END;
    ''',
    'vendas_bloquear_devolucao_vinculada_delete': '''
        CREATE TRIGGER vendas_bloquear_devolucao_vinculada_delete
        BEFORE DELETE ON estoque_movimentacaoestoque
        FOR EACH ROW
        WHEN OLD.movimento_saida_estornado_id IS NOT NULL
        BEGIN
            SELECT RAISE(ABORT, 'Devolucao de venda nao pode ser excluida.');
        END;
    ''',
}

POSTGRES_FUNCTION = '''
CREATE OR REPLACE FUNCTION vendas_proteger_devolucao_estoque()
RETURNS trigger AS $$
DECLARE
    saida_atual estoque_movimentacaoestoque%ROWTYPE;
    item_atual vendas_itemvenda%ROWTYPE;
    venda_atual vendas_venda%ROWTYPE;
    estoque_atual estoque_estoque%ROWTYPE;
    venda_id_inicial bigint;
BEGIN
    IF TG_OP = 'INSERT' AND NEW.movimento_saida_estornado_id IS NOT NULL THEN
        SELECT item.venda_id INTO venda_id_inicial
        FROM estoque_movimentacaoestoque saida
        JOIN vendas_itemvenda item ON item.id = saida.item_venda_id
        WHERE saida.id = NEW.movimento_saida_estornado_id
          AND saida.tipo_movimento = 'saida';

        IF NOT FOUND THEN
            RAISE EXCEPTION 'Saida vinculada a devolucao nao encontrada.';
        END IF;

        SELECT * INTO venda_atual
        FROM vendas_venda
        WHERE id = venda_id_inicial
        FOR UPDATE;

        SELECT item.* INTO item_atual
        FROM vendas_itemvenda item
        JOIN estoque_movimentacaoestoque saida ON saida.item_venda_id = item.id
        WHERE saida.id = NEW.movimento_saida_estornado_id
        FOR UPDATE OF item NOWAIT;

        SELECT * INTO saida_atual
        FROM estoque_movimentacaoestoque
        WHERE id = NEW.movimento_saida_estornado_id
        FOR UPDATE;

        IF NOT FOUND
           OR item_atual.venda_id IS DISTINCT FROM venda_atual.id
           OR saida_atual.item_venda_id IS DISTINCT FROM item_atual.id
           OR saida_atual.tipo_movimento IS DISTINCT FROM 'saida'
           OR NEW.item_venda_id IS NOT NULL
           OR NEW.tipo_movimento IS DISTINCT FROM 'devolucao'
           OR NEW.empresa_id IS DISTINCT FROM venda_atual.empresa_id
           OR NEW.produto_id IS DISTINCT FROM saida_atual.produto_id
           OR NEW.quantidade IS DISTINCT FROM saida_atual.quantidade THEN
            RAISE EXCEPTION 'Devolucao vinculada nao reflete a saida da venda.';
        END IF;

        SELECT * INTO estoque_atual
        FROM estoque_estoque
        WHERE produto_id = NEW.produto_id
        FOR UPDATE;

        IF NOT FOUND THEN
            RAISE EXCEPTION 'Estoque da devolucao nao encontrado.';
        END IF;

        UPDATE estoque_estoque
        SET quantidade = quantidade + NEW.quantidade
        WHERE id = estoque_atual.id;
        RETURN NEW;
    END IF;

    IF TG_OP = 'DELETE' THEN
        IF OLD.movimento_saida_estornado_id IS NOT NULL THEN
            RAISE EXCEPTION 'Devolucao de venda nao pode ser excluida.';
        END IF;
        RETURN OLD;
    END IF;

    IF NEW.movimento_saida_estornado_id IS DISTINCT FROM OLD.movimento_saida_estornado_id
       OR (
           OLD.movimento_saida_estornado_id IS NOT NULL AND (
               NEW.item_venda_id IS DISTINCT FROM OLD.item_venda_id
               OR NEW.empresa_id IS DISTINCT FROM OLD.empresa_id
               OR NEW.produto_id IS DISTINCT FROM OLD.produto_id
               OR NEW.tipo_movimento IS DISTINCT FROM OLD.tipo_movimento
               OR NEW.quantidade IS DISTINCT FROM OLD.quantidade
           )
       ) THEN
        RAISE EXCEPTION 'Devolucao de venda e imutavel.';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
'''

POSTGRES_TRIGGERS = [
    '''CREATE TRIGGER vendas_aplicar_devolucao_vinculada_insert
       BEFORE INSERT ON estoque_movimentacaoestoque
       FOR EACH ROW EXECUTE FUNCTION vendas_proteger_devolucao_estoque();''',
    '''CREATE TRIGGER vendas_bloquear_devolucao_vinculada
       BEFORE UPDATE OR DELETE ON estoque_movimentacaoestoque
       FOR EACH ROW EXECUTE FUNCTION vendas_proteger_devolucao_estoque();''',
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
                'DROP TRIGGER IF EXISTS vendas_aplicar_devolucao_vinculada_insert '
                'ON estoque_movimentacaoestoque'
            )
            cursor.execute(
                'DROP TRIGGER IF EXISTS vendas_bloquear_devolucao_vinculada '
                'ON estoque_movimentacaoestoque'
            )
            cursor.execute(
                'DROP FUNCTION IF EXISTS vendas_proteger_devolucao_estoque()'
            )


class Migration(migrations.Migration):
    dependencies = [
        ('estoque', '0005_movimentacao_saida_estornada'),
        ('vendas', '0007_bloquear_saida_estado_terminal'),
    ]

    operations = [
        migrations.RunPython(criar_triggers, remover_triggers),
    ]
