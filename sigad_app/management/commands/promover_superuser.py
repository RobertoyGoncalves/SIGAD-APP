import os

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Promove um usuário existente a superusuário/staff, a partir de uma variável de ambiente.'

    def handle(self, *args, **options):
        username = os.getenv('DJANGO_PROMOTE_SUPERUSER', '').strip()

        if not username:
            self.stdout.write('DJANGO_PROMOTE_SUPERUSER não definido, pulando.')
            return

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(f'Usuário "{username}" não encontrado, pulando.')
            return

        if user.is_superuser and user.is_staff:
            self.stdout.write(f'Usuário "{username}" já é superusuário, pulando.')
            return

        user.is_staff = True
        user.is_superuser = True
        user.save()
        self.stdout.write(f'Usuário "{username}" promovido a superusuário com sucesso.')
