# Generated by Django 5.0.6 on 2024-06-13 23:12

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Fabricante',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome_fantasia', models.CharField(max_length=100)),
                ('razao_social', models.CharField(max_length=100)),
                ('cnpj', models.CharField(max_length=18)),
                ('endereco', models.TextField()),
                ('telefone', models.CharField(max_length=15)),
                ('email', models.EmailField(max_length=254)),
                ('vendedor', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Grupo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100)),
                ('descricao', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='SubGrupo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100)),
                ('descricao', models.TextField()),
                ('grupo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='vendas.grupo')),
            ],
        ),
        migrations.CreateModel(
            name='Produto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100)),
                ('descricao', models.TextField()),
                ('preco_custo', models.DecimalField(decimal_places=2, max_digits=10)),
                ('preco_venda', models.DecimalField(decimal_places=2, max_digits=10)),
                ('peso', models.DecimalField(decimal_places=2, max_digits=5)),
                ('quantidade_comprado', models.IntegerField()),
                ('quantidade_vendido', models.IntegerField(default=0)),
                ('fabricante', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='vendas.fabricante')),
                ('grupo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='vendas.grupo')),
                ('subgrupo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='vendas.subgrupo')),
            ],
        ),
        migrations.CreateModel(
            name='Venda',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantidade', models.IntegerField()),
                ('data_hora', models.DateTimeField(auto_now_add=True)),
                ('produto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='vendas.produto')),
            ],
        ),
    ]
