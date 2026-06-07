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
        # fallback se o render ainda nao injetou secret_key neste deploy
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


def _is_truthy(val: str) -> bool:
    return val.strip().lower() in ('1', 'true', 'yes', 'on')


def _postgres_from_url(url: str) -> dict:
    u = urlparse(url.strip())
    if u.scheme not in ('postgres', 'postgresql'):
        raise ValueError('DATABASE_URL deve começar com postgres:// ou postgresql://')
    name = (u.path or '').lstrip('/') or 'postgres'
    host = u.hostname or ''
    sslmode = os.getenv('DATABASE_SSLMODE', '').strip()
    if not sslmode:
        sslmode = 'disable' if host.endswith('.railway.internal') else 'require'
    config = {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': name,
        'USER': unquote(u.username or ''),
        'PASSWORD': unquote(u.password or ''),
        'HOST': host,
        'PORT': str(u.port or 5432),
        'CONN_MAX_AGE': 60,
    }
    if sslmode != 'disable':
        config['OPTIONS'] = {'sslmode': sslmode}
    return config


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
DEBUG = _is_truthy(os.getenv('DEBUG', 'True'))

ALLOWED_HOSTS = [
    h.strip()
    for h in os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
    if h.strip()
]
_render_host = os.getenv('RENDER_EXTERNAL_HOSTNAME', '').strip()
_railway_host = os.getenv('RAILWAY_PUBLIC_DOMAIN', '').strip()
_on_railway = bool(os.getenv('RAILWAY_ENVIRONMENT', '').strip()) or bool(_railway_host)

for _auto_host in (_render_host, _railway_host):
    if _auto_host and _auto_host not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(_auto_host)

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

_csrf_origins: list[str] = []
if _render_host:
    _csrf_origins.append(f'https://{_render_host}')
if _railway_host:
    _csrf_origins.append(f'https://{_railway_host}')
if extra := os.getenv('CSRF_TRUSTED_ORIGINS', '').strip():
    for origin in extra.split(','):
        origin = origin.strip()
        if origin and origin not in _csrf_origins:
            _csrf_origins.append(origin)
if _csrf_origins:
    CSRF_TRUSTED_ORIGINS = _csrf_origins

if _is_truthy(os.getenv('RENDER', '')) or _on_railway:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

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

if not DEBUG:
    STORAGES = {
        'default': {
            'BACKEND': 'django.core.files.storage.FileSystemStorage',
        },
        'staticfiles': {
            'BACKEND': 'whitenoise.storage.CompressedStaticFilesStorage',
        },
    }

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
