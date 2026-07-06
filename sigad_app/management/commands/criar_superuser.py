import os

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Cria um superusuário a partir de variáveis de ambiente, se ele ainda não existir.'

    def handle(self, *args, **options):
        username = os.getenv('DJANGO_SUPERUSER_USERNAME', '').strip()
        email = os.getenv('DJANGO_SUPERUSER_EMAIL', '').strip()
        password = os.getenv('DJANGO_SUPERUSER_PASSWORD', '').strip()

        if not username or not password:
            self.stdout.write('DJANGO_SUPERUSER_USERNAME/PASSWORD não definidos, pulando.')
            return

        if User.objects.filter(username=username).exists():
            self.stdout.write(f'Usuário "{username}" já existe, pulando.')
            return

        User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(f'Superusuário "{username}" criado com sucesso.')
