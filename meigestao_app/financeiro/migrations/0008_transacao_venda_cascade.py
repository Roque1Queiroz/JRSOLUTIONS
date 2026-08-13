# Generated manually for durable sale/transaction lifecycle.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('financeiro', '0007_reciboreembolso_prioridade'),
        ('vendas', '0004_proteger_vendas_liquidadas'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transacao',
            name='venda',
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='transacao_financeira',
                to='vendas.venda',
            ),
        ),
    ]
