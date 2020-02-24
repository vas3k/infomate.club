import os
from datetime import timedelta

from random import random

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

DEBUG = os.getenv("DEBUG", True)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = "wow so secret"
ALLOWED_HOSTS = ["127.0.0.1", "localhost", "0.0.0.0", "vas3k.ru", "infomate.club"]

INSTALLED_APPS = [
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "django_bleach",
    "auth",
    "boards",
    "parsing"
]

MIDDLEWARE = [
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "infomate.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(BASE_DIR, "templates"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "boards.context_processors.settings_processor",
                "auth.context_processors.me",
            ],
        },
    },
]

WSGI_APPLICATION = "infomate.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "infomate",
        "USER": "postgres",  # redefined in private_settings.py
        "PASSWORD": "postgres",
        "HOST": "postgres",
        "PORT": "5432",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "ru-ru"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = False

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)

STATIC_URL = "/static/"
CSS_HASH = str(random())

# Cache

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}
STATIC_PAGE_CACHE_SECONDS = 5 * 60  # 5 min
BOARD_CACHE_SECONDS = 10 * 60  # 10 min

# App settings

APP_NAME = "Infomate"
APP_TITLE = "Читай интернет нормально"
APP_DESCRIPTION = APP_TITLE
APP_HOST = "https://infomate.club"

JWT_SECRET = "wow so secret"  # should be the same as on vas3k.ru
JWT_ALGORITHM = "HS256"
JWT_EXP_TIMEDELTA = timedelta(days=120)

AUTH_COOKIE_NAME = "jwt"
AUTH_COOKIE_MAX_AGE = 300 * 24 * 60 * 60  # 300 days
AUTH_REDIRECT_URL = "https://vas3k.ru/auth/external/"
AUTH_FAILED_REDIRECT_URL = "https://vas3k.ru/auth/login/"

SENTRY_DSN = None

MEDIA_UPLOAD_URL = "https://i.vas3k.ru/upload/"
MEDIA_UPLOAD_CODE = None  # should be set in private_settings.py

TELEGRAM_APP_ID = None  # should set in private_settings.py
TELEGRAM_APP_HASH = None  # should set in private_settings.py
TELEGRAM_SESSION_FILE = None  # should set in private settings.py
TELEGRAM_CACHE_SECONDS = 10 * 60  # 10 min

BLEACH_STRIP_TAGS = True

try:
    # poor mans' private settings
    # As due to obvious reasons this file is missing in the repository, suppress the following 'pyflakes' error codes:
    # - F401 'infomate.private_settings.*' imported but unused
    # - F403 'from infomate.private_settings import *' used; unable to detect undefined names
    from infomate.private_settings import *  # noqa: F401 F403
except ImportError:
    pass


if SENTRY_DSN and not DEBUG:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()]
    )
