# Generated manually for idempotent sale stock effects.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('estoque', '0003_categoria_empresa_estoque_empresa_and_more'),
        ('vendas', '0004_proteger_vendas_liquidadas'),
    ]

    operations = [
        migrations.AddField(
            model_name='movimentacaoestoque',
            name='item_venda',
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='movimento_saida_estoque',
                to='vendas.itemvenda',
            ),
        ),
    ]
