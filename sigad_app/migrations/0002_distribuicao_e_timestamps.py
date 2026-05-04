import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sigad_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='beneficiario',
            name='criado_em',
            field=models.DateTimeField(
                auto_now_add=True,
                default=django.utils.timezone.now,
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='itemestoque',
            name='criado_em',
            field=models.DateTimeField(
                auto_now_add=True,
                default=django.utils.timezone.now,
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='itemestoque',
            name='categoria',
            field=models.CharField(
                choices=[
                    ('Alimentos', 'Alimentos'),
                    ('Higiene', 'Higiene'),
                    ('Roupas', 'Roupas'),
                    ('Limpeza', 'Limpeza'),
                    ('Outros', 'Outros'),
                ],
                max_length=30,
            ),
        ),
        migrations.CreateModel(
            name='Distribuicao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('registrado_em', models.DateTimeField(auto_now_add=True)),
                (
                    'beneficiario',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='distribuicoes',
                        to='sigad_app.beneficiario',
                    ),
                ),
            ],
            options={
                'ordering': ['-registrado_em'],
            },
        ),
        migrations.CreateModel(
            name='LinhaDistribuicao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantidade', models.PositiveIntegerField()),
                (
                    'distribuicao',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='linhas',
                        to='sigad_app.distribuicao',
                    ),
                ),
                (
                    'item_estoque',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='linhas_distribuicao',
                        to='sigad_app.itemestoque',
                    ),
                ),
            ],
            options={
                'ordering': ['id'],
            },
        ),
    ]
