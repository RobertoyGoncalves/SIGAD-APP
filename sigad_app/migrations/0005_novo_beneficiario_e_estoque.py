# Cria o novo modelo Beneficiario (quem DOA),
# remove o CharField doador de ItemEstoque e adiciona FK para Beneficiario.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sigad_app', '0004_renomear_beneficiario_para_beneficiado'),
    ]

    operations = [
        migrations.CreateModel(
            name='Beneficiario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=120)),
                ('cpf', models.CharField(blank=True, max_length=14)),
                ('telefone', models.CharField(blank=True, max_length=20)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('endereco', models.CharField(blank=True, max_length=255)),
                ('observacoes', models.TextField(blank=True)),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Beneficiário',
                'verbose_name_plural': 'Beneficiários',
                'ordering': ['-criado_em'],
            },
        ),
        migrations.RemoveField(
            model_name='itemestoque',
            name='doador',
        ),
        migrations.AddField(
            model_name='itemestoque',
            name='beneficiario',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='itens_doados',
                to='sigad_app.beneficiario',
                verbose_name='Beneficiário (quem doou)',
            ),
        ),
    ]
