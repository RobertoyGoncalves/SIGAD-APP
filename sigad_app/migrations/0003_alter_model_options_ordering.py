# migracao django 5.2.13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sigad_app', '0002_distribuicao_e_timestamps'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='beneficiario',
            options={'ordering': ['-criado_em']},
        ),
        migrations.AlterModelOptions(
            name='itemestoque',
            options={'ordering': ['-criado_em']},
        ),
    ]
