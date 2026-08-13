from django.db import migrations


SQLITE_INSERT_TRIGGER = '''
CREATE TRIGGER vendas_bloquear_insert_estado_terminal
BEFORE INSERT ON vendas_venda
FOR EACH ROW
WHEN NEW.status IN ('entregue', 'cancelada')
BEGIN
    SELECT RAISE(ABORT, 'Venda nova nao pode nascer em estado terminal.');
END;
'''

SQLITE_TRIGGER = '''
CREATE TRIGGER vendas_bloquear_saida_estado_terminal
BEFORE UPDATE OF status ON vendas_venda
FOR EACH ROW
WHEN NOT (
    NEW.status IS OLD.status
    OR (OLD.status = 'rascunho' AND NEW.status IN ('confirmada', 'cancelada'))
    OR (OLD.status = 'confirmada' AND NEW.status = 'entregue')
    OR (
        OLD.status = 'confirmada'
        AND NEW.status = 'cancelada'
        AND NOT EXISTS (
            SELECT 1 FROM fiscal_notafiscal nota
            WHERE nota.venda_id = NEW.id AND nota.status = 'emitida'
        )
        AND NOT EXISTS (
            SELECT 1 FROM financeiro_transacao transacao
            WHERE transacao.venda_id = NEW.id
        )
        AND NOT EXISTS (
            SELECT 1
            FROM vendas_itemvenda item
            WHERE item.venda_id = NEW.id
              AND item.produto_vinculado_id IS NOT NULL
              AND NOT EXISTS (
                  SELECT 1
                  FROM estoque_movimentacaoestoque saida
                  JOIN estoque_movimentacaoestoque devolucao
                    ON devolucao.movimento_saida_estornado_id = saida.id
                  WHERE saida.item_venda_id = item.id
                    AND saida.tipo_movimento = 'saida'
                    AND saida.produto_id = item.produto_vinculado_id
                    AND saida.quantidade = item.quantidade
                    AND devolucao.tipo_movimento = 'devolucao'
                    AND devolucao.empresa_id = NEW.empresa_id
                    AND devolucao.produto_id = item.produto_vinculado_id
                    AND devolucao.quantidade = item.quantidade
              )
        )
    )
)
BEGIN
    SELECT RAISE(ABORT, 'Transicao de estado da venda nao permitida.');
END;
'''

POSTGRES_INSERT_FUNCTION = '''
CREATE OR REPLACE FUNCTION vendas_bloquear_insert_estado_terminal()
RETURNS trigger AS $$
BEGIN
    IF NEW.status IN ('entregue', 'cancelada') THEN
        RAISE EXCEPTION 'Venda nova nao pode nascer em estado terminal.';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
'''

POSTGRES_INSERT_TRIGGER = '''
CREATE TRIGGER vendas_bloquear_insert_estado_terminal
BEFORE INSERT ON vendas_venda
FOR EACH ROW EXECUTE FUNCTION vendas_bloquear_insert_estado_terminal();
'''

POSTGRES_FUNCTION = '''
CREATE OR REPLACE FUNCTION vendas_bloquear_saida_estado_terminal()
RETURNS trigger AS $$
BEGIN
    IF NOT (
        NEW.status IS NOT DISTINCT FROM OLD.status
        OR (OLD.status = 'rascunho' AND NEW.status IN ('confirmada', 'cancelada'))
        OR (OLD.status = 'confirmada' AND NEW.status = 'entregue')
        OR (
            OLD.status = 'confirmada'
            AND NEW.status = 'cancelada'
            AND NOT EXISTS (
                SELECT 1 FROM fiscal_notafiscal nota
                WHERE nota.venda_id = NEW.id AND nota.status = 'emitida'
            )
            AND NOT EXISTS (
                SELECT 1 FROM financeiro_transacao transacao
                WHERE transacao.venda_id = NEW.id
            )
            AND NOT EXISTS (
                SELECT 1
                FROM vendas_itemvenda item
                WHERE item.venda_id = NEW.id
                  AND item.produto_vinculado_id IS NOT NULL
                  AND NOT EXISTS (
                      SELECT 1
                      FROM estoque_movimentacaoestoque saida
                      JOIN estoque_movimentacaoestoque devolucao
                        ON devolucao.movimento_saida_estornado_id = saida.id
                      WHERE saida.item_venda_id = item.id
                        AND saida.tipo_movimento = 'saida'
                        AND saida.produto_id = item.produto_vinculado_id
                        AND saida.quantidade = item.quantidade
                        AND devolucao.tipo_movimento = 'devolucao'
                        AND devolucao.empresa_id = NEW.empresa_id
                        AND devolucao.produto_id = item.produto_vinculado_id
                        AND devolucao.quantidade = item.quantidade
                  )
            )
        )
    ) THEN
        RAISE EXCEPTION 'Transicao de estado da venda nao permitida.';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
'''

POSTGRES_TRIGGER = '''
CREATE TRIGGER vendas_bloquear_saida_estado_terminal
BEFORE UPDATE OF status ON vendas_venda
FOR EACH ROW EXECUTE FUNCTION vendas_bloquear_saida_estado_terminal();
'''


def criar_protecao(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        if schema_editor.connection.vendor == 'sqlite':
            cursor.execute(SQLITE_INSERT_TRIGGER)
            cursor.execute(SQLITE_TRIGGER)
        elif schema_editor.connection.vendor == 'postgresql':
            cursor.execute(POSTGRES_INSERT_FUNCTION)
            cursor.execute(POSTGRES_INSERT_TRIGGER)
            cursor.execute(POSTGRES_FUNCTION)
            cursor.execute(POSTGRES_TRIGGER)


def remover_protecao(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        if schema_editor.connection.vendor == 'sqlite':
            cursor.execute('DROP TRIGGER IF EXISTS vendas_bloquear_insert_estado_terminal')
            cursor.execute('DROP TRIGGER IF EXISTS vendas_bloquear_saida_estado_terminal')
        elif schema_editor.connection.vendor == 'postgresql':
            cursor.execute(
                'DROP TRIGGER IF EXISTS vendas_bloquear_insert_estado_terminal '
                'ON vendas_venda'
            )
            cursor.execute(
                'DROP TRIGGER IF EXISTS vendas_bloquear_saida_estado_terminal '
                'ON vendas_venda'
            )
            cursor.execute(
                'DROP FUNCTION IF EXISTS vendas_bloquear_insert_estado_terminal()'
            )
            cursor.execute(
                'DROP FUNCTION IF EXISTS vendas_bloquear_saida_estado_terminal()'
            )


class Migration(migrations.Migration):
    dependencies = [
        ('estoque', '0005_movimentacao_saida_estornada'),
        ('fiscal', '0003_notafiscal_fiscal_nota_numero_b662a5_idx_and_more'),
        ('vendas', '0006_corrigir_trigger_liquidacao_postgresql'),
    ]

    operations = [
        migrations.RunPython(criar_protecao, remover_protecao),
    ]
