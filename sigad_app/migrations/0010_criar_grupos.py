"""
Req 2 — data migration: cria os grupos "Gestores" e "Operadores" no banco.

- Gestores: podem acessar UsuarioListView e EstoqueBaixoView (GroupRequiredMixin)
- Operadores: grupo operacional para futura expansão de permissões

Os grupos ficam gerenciáveis via /admin/auth/group/ (registrado automaticamente
pelo django.contrib.auth).
"""
from django.db import migrations


def criar_grupos(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.get_or_create(name='Gestores')
    Group.objects.get_or_create(name='Operadores')


def desfazer_grupos(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name__in=['Gestores', 'Operadores']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('sigad_app', '0009_rename_beneficiario_to_doador'),
        # garante que a tabela auth_group existe antes
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.RunPython(criar_grupos, desfazer_grupos),
    ]
