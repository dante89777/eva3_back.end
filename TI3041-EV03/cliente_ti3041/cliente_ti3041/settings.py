"""
Configuracion del Proyecto 2 - Cliente web que consume la API TI3041.

Este proyecto NO utiliza base de datos: la sesion se almacena en cookies
firmadas y los datos se obtienen desde la API del Proyecto 1.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-c^hr@d#j7oz9-t6$8ui+yhm9w=x$0+!mh3t7ozrfqn^3n6w(v)'

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'web',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'cliente_ti3041.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
            ],
        },
    },
]

WSGI_APPLICATION = 'cliente_ti3041.wsgi.application'

# Proyecto 2 sin base de datos: la sesion viaja en una cookie firmada.
DATABASES = {}
MIGRATION_MODULES = {'sessions': None}
SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = 'es-cl'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# URL base de la API del Proyecto 1.
API_BASE_URL = os.environ.get('API_BASE_URL', 'http://127.0.0.1:8000/api')
API_TIMEOUT = 10

SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'
