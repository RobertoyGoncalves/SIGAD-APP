from pathlib import Path
import hashlib
import os
from urllib.parse import unquote, urlparse

BASE_DIR = Path(__file__).resolve().parent.parent

try:
    from dotenv import load_dotenv

    load_dotenv(BASE_DIR / '.env')
except ImportError:
    pass


def _secret_key_from_env() -> str:
    raw = (os.getenv('SECRET_KEY') or '').strip()
    if raw and raw != 'django-insecure-sigad-dev-key':
        return raw
    if os.getenv('RENDER', '').strip().lower() in ('1', 'true', 'yes'):
        # generateValue as vezes so existe apos o 1o ciclo; fallback estavel por deploy (mesmo valor em todos os workers)
        seed = '|'.join(
            (
                os.getenv('RENDER_EXTERNAL_HOSTNAME', ''),
                os.getenv('RENDER_SERVICE_NAME', ''),
                os.getenv('RENDER_GIT_COMMIT', ''),
                'sigad',
            )
        )
        return hashlib.sha256(seed.encode('utf-8')).hexdigest()
    return 'django-insecure-sigad-dev-key'


SECRET_KEY = _secret_key_from_env()


def _postgres_from_url(url: str) -> dict:
    u = urlparse(url.strip())
    if u.scheme not in ('postgres', 'postgresql'):
        raise ValueError('DATABASE_URL deve começar com postgres:// ou postgresql://')
    name = (u.path or '').lstrip('/') or 'postgres'
    return {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': name,
        'USER': unquote(u.username or ''),
        'PASSWORD': unquote(u.password or ''),
        'HOST': u.hostname or '',
        'PORT': str(u.port or 5432),
        'OPTIONS': {'sslmode': 'require'},
        'CONN_MAX_AGE': 60,
    }


def _postgres_from_env() -> dict | None:
    url = os.getenv('DATABASE_URL', '').strip()
    if url:
        return _postgres_from_url(url)
    host = os.getenv('SUPABASE_DB_HOST', '').strip()
    if not host:
        return None
    return {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('SUPABASE_DB_NAME', 'postgres'),
        'USER': os.getenv('SUPABASE_DB_USER', 'postgres'),
        'PASSWORD': os.getenv('SUPABASE_DB_PASSWORD', ''),
        'HOST': host,
        'PORT': os.getenv('SUPABASE_DB_PORT', '5432'),
        'OPTIONS': {'sslmode': 'require'},
        'CONN_MAX_AGE': 60,
    }
DEBUG = os.getenv('DEBUG', 'True').strip().lower() in ('1', 'true', 'yes', 'on')

ALLOWED_HOSTS = [
    h.strip()
    for h in os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
    if h.strip()
]
_render_host = os.getenv('RENDER_EXTERNAL_HOSTNAME', '').strip()
if _render_host and _render_host not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(_render_host)

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

if os.getenv('RENDER', '').strip().lower() in ('1', 'true', 'yes'):
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    if _render_host:
        origin = f'https://{_render_host}'
        CSRF_TRUSTED_ORIGINS = [origin]
        if os.getenv('CSRF_TRUSTED_ORIGINS'):
            CSRF_TRUSTED_ORIGINS.extend(
                x.strip()
                for x in os.getenv('CSRF_TRUSTED_ORIGINS', '').split(',')
                if x.strip() and x.strip() not in CSRF_TRUSTED_ORIGINS
            )
elif (extra := os.getenv('CSRF_TRUSTED_ORIGINS', '').strip()):
    CSRF_TRUSTED_ORIGINS = [x.strip() for x in extra.split(',') if x.strip()]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'sigad_app',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'sigad.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'sigad.wsgi.application'

_pg = _postgres_from_env()
if _pg:
    DATABASES = {'default': _pg}
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'sigad_app' / 'static']

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
