# Renomeia Beneficiario (quem doa) → Doador e o FK em ItemEstoque.

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sigad_app', '0008_beneficiado_usuario_beneficiario_usuario_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Beneficiario',
            new_name='Doador',
        ),
        migrations.RenameField(
            model_name='itemestoque',
            old_name='beneficiario',
            new_name='doador',
        ),
        migrations.AlterField(
            model_name='doador',
            name='usuario',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='doadores',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name='itemestoque',
            name='doador',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='itens_doados',
                to='sigad_app.doador',
                verbose_name='Doador (quem doou)',
            ),
        ),
        migrations.AlterModelOptions(
            name='doador',
            options={'ordering': ['-criado_em'], 'verbose_name': 'Doador', 'verbose_name_plural': 'Doadores'},
        ),
    ]
