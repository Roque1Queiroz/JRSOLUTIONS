from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('vendas', '0002_remove_itemvenda_atualizado_em_and_more'),
        ('financeiro', '0003_reciboreembolso_transacao'),
    ]

    operations = [
        migrations.AddField(
            model_name='transacao',
            name='venda',
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='transacao_financeira',
                to='vendas.venda',
            ),
        ),
    ]
