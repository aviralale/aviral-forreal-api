from pathlib import Path
from dotenv import load_dotenv
import os, dj_database_url

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ['SECRET_KEY']
DEBUG = os.getenv('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'django_filters',
    'blog',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'
TEMPLATES = [{'BACKEND': 'django.template.backends.django.DjangoTemplates',
              'DIRS': [], 'APP_DIRS': True,
              'OPTIONS': {'context_processors': [
                  'django.template.context_processors.debug',
                  'django.template.context_processors.request',
                  'django.contrib.auth.context_processors.auth',
                  'django.contrib.messages.context_processors.messages',
              ]}}]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': dj_database_url.config(
        default=f'sqlite:///{BASE_DIR}/db.sqlite3'
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
}

CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:3000').split(',')

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kathmandu'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# --- Media: conversion + storage --------------------------------------------
# Uploaded images are re-encoded to a compact web format before storage
# (see blog/images.py). This applies in every environment.
IMAGE_UPLOAD_FORMAT = os.getenv('IMAGE_UPLOAD_FORMAT', 'webp')  # 'webp' | 'avif'
IMAGE_UPLOAD_QUALITY = int(os.getenv('IMAGE_UPLOAD_QUALITY', '80'))

# In production (DEBUG off), point media at a Cloudflare R2 bucket
# (S3-compatible) by setting the R2_* vars. In dev — or with the vars unset —
# media stays on the local disk and is served from /media, so local uploads
# never touch the production bucket even when the creds are present.
R2_BUCKET_NAME = os.getenv('R2_BUCKET_NAME')
R2_ACCOUNT_ID = os.getenv('R2_ACCOUNT_ID')

if R2_BUCKET_NAME and R2_ACCOUNT_ID and not DEBUG:
    _r2_options = {
        'bucket_name': R2_BUCKET_NAME,
        'access_key': os.environ['R2_ACCESS_KEY_ID'],
        'secret_key': os.environ['R2_SECRET_ACCESS_KEY'],
        'endpoint_url': os.getenv(
            'R2_ENDPOINT_URL',
            f'https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com',
        ),
        'region_name': 'auto',
        'default_acl': None,  # R2 ignores ACLs; don't send one
        'file_overwrite': False,  # unique names, never clobber
        'signature_version': 's3v4',
        # Long-lived caching — names are unique, so safe to keep.
        'object_parameters': {
            'CacheControl': 'public, max-age=31536000, immutable',
        },
    }
    # Prefer a public host (custom domain or pub-*.r2.dev) serving clean,
    # unsigned URLs. Until one is set, fall back to signed endpoint URLs so
    # uploads still work — just set R2_PUBLIC_DOMAIN for production.
    _r2_public = os.getenv('R2_PUBLIC_DOMAIN')
    if _r2_public:
        # Accept either a bare host or a full URL; custom_domain wants the host.
        _r2_public = _r2_public.split('://', 1)[-1].strip('/')
        _r2_options['custom_domain'] = _r2_public  # https://<domain>/<key>
        _r2_options['querystring_auth'] = False
    else:
        _r2_options['querystring_auth'] = True

    STORAGES = {
        'default': {
            'BACKEND': 'storages.backends.s3.S3Storage',
            'OPTIONS': _r2_options,
        },
        'staticfiles': {
            'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
        },
    }
else:
    STORAGES = {
        'default': {
            'BACKEND': 'django.core.files.storage.FileSystemStorage',
        },
        'staticfiles': {
            'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
        },
    }

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
