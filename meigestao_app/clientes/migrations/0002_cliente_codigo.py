# -*- coding: utf-8 -*-
# Spec codigo-cliente: Cliente ganha codigo por empresa + SequenciaCliente.
# Preenche os clientes existentes em ordem de criado_em + id (nao zera o id interno).
from django.db import migrations, models
import django.db.models.deletion


def preencher_codigos(apps, schema_editor):
    Cliente = apps.get_model('clientes', 'Cliente')
    Empresa = apps.get_model('core', 'Empresa')
    for empresa in Empresa.objects.all():
        clientes = list(
            Cliente.objects.filter(empresa=empresa).order_by('criado_em', 'id')
        )
        for indice, cliente in enumerate(clientes, start=1):
            if cliente.codigo is None:
                cliente.codigo = indice
                cliente.save(update_fields=['codigo'])


def reverter_codigos(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('clientes', '0001_initial'),
        ('core', '0007_empresa_asaas_customer_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='cliente',
            name='codigo',
            field=models.PositiveIntegerField(default=1, verbose_name='Código'),
            preserve_default=False,
        ),
        migrations.AddConstraint(
            model_name='cliente',
            constraint=models.UniqueConstraint(
                fields=('empresa', 'codigo'),
                name='uniq_cliente_empresa_codigo',
            ),
        ),
        migrations.CreateModel(
            name='SequenciaCliente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ultimo', models.PositiveIntegerField(default=0)),
                ('empresa', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='sequencia_cliente',
                    to='core.empresa',
                )),
            ],
            options={
                'verbose_name': 'Sequência de código do cliente',
                'verbose_name_plural': 'Sequências de código do cliente',
            },
        ),
        migrations.RunPython(preencher_codigos, reverter_codigos),
    ]