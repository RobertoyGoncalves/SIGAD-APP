"""
Req 2 — data migration: cria os grupos "Gestores" e "Operadores" no banco.

- Gestores: acesso a UsuarioListView (gerenciar contas) e EstoqueBaixoView
  (alerta de itens com estoque baixo) via GroupRequiredMixin.
- Operadores: acesso a registrar_item (cadastrar itens no estoque) via
  @user_passes_test(lambda u: u.is_superuser or u.groups.filter(Gestores|Operadores)).
  Reflete a separação natural do domínio: operadores fazem o trabalho dia a dia
  (registrar doações/itens), gestores têm visão gerencial do sistema.

Superusuários ignoram a verificação de grupo em ambas as views.
Os grupos ficam gerenciáveis via /admin/auth/group/ (registro automático do Django).
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
