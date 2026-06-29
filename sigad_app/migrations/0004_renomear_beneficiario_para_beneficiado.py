# Renomeia o modelo Beneficiario (quem recebia) para Beneficiado (quem recebe),
# e renomeia o campo FK em Distribuicao de beneficiario para beneficiado.

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sigad_app', '0003_alter_model_options_ordering'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Beneficiario',
            new_name='Beneficiado',
        ),
        migrations.RenameField(
            model_name='distribuicao',
            old_name='beneficiario',
            new_name='beneficiado',
        ),
    ]
