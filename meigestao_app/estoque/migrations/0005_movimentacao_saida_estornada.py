from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('estoque', '0004_movimentacaoestoque_item_venda'),
    ]

    operations = [
        migrations.AddField(
            model_name='movimentacaoestoque',
            name='movimento_saida_estornado',
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='movimento_devolucao_estoque',
                to='estoque.movimentacaoestoque',
            ),
        ),
    ]
