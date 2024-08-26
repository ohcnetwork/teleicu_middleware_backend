"""
Django settings for middleware project.

Generated by 'django-admin startproject' using Django 5.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from authlib.jose import JsonWebKey
import base64

from pathlib import Path
import environ
import json

from middleware.utils import generate_encoded_jwks

env = environ.Env()
environ.Env.read_env()

# import django

# django.setup()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-^z7t*bx*ph&x(1t2s^v%coj-&a7qc0ws0laefrmmqv!tyx(_7^"
APPEND_SLASH = False
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*", "ws://127.0.0.1", "127.0.0.1", "teleicu_middleware:8090"]
CORS_ALLOW_ALL_ORIGINS = True
# CORS_ALLOWED_ORIGINS = [
#     "https://care-dev-middleware.10bedicu.in",
# ]
# Application definition

INSTALLED_APPS = [
    "daphne",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "middleware",
    "django_extensions",
    "django_celery_beat",
    "drf_spectacular",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "middleware.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "middleware.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Kolkata"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "/static/"
STATICFILES_DIRS = [
    BASE_DIR / "static",
    "middleware/static",
]

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.BasicAuthentication",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

ASGI_APPLICATION = "middleware.asgi.application"

CHANNEL_LAYERS = {"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}


CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis:6379/1",  # Redis server location
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}


# Configs
CARE_URL = env("CARE_URL")
CARE_API = env("CARE_API")
FACILITY_ID = env("FACILITY_ID")
CARE_JWK_URL = env("CARE_JWK_URL")
CARE_VERIFY_TOKEN_URL = env("CARE_VERIFY_TOKEN_URL")


JWKS = JsonWebKey.import_key_set(
    json.loads(base64.b64decode(env("JWKS_BASE64", default=generate_encoded_jwks())))
)
CELERY_BROKER_URL = "redis://redis:6379"

CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

HOST_NAME = env("HOST_NAME")
CSRF_TRUSTED_ORIGINS = ["https://care-dev-middleware.10bedicu.in"]

# Observations
REDIS_OBSERVATIONS_KEY = env("REDIS_OBSERVATIONS_KEY")
UPDATE_INTERVAL = env.int("UPDATE_INTERVAL", default=60)


# Cameras
WSDL_PATH = env("WSDL_PATH")
HOSTNAME = env("HOSTNAME")
ONVIF_USERNAME = env("ONVIF_USERNAME")
PASSWORD = env("PASSWORD")
PORT = env("PORT")

CAMERA_LOCK_KEY = env("CAMERA_LOCK_KEY")
CAMERA_LOCK_TIMEOUT = env("CAMERA_LOCK_TIMEOUT")


# s3
S3_ACCESS_KEY_ID = ""
S3_SECRET_ACCESS_KEY = ""
S3_ENDPOINT_URL = ""
S3_BUCKET_NAME = ""


# redis status keys
MONITOR_STATUS_KEY = env("MONITOR_STATUS_KEY")
CAMERA_STATUS_KEY = env("CAMERA_STATUS_KEY")

# Drf spectacular
SPECTACULAR_SETTINGS = {
    "TITLE": "Teleicu Middleware",
    "DESCRIPTION": "Teleicu Middleware Api Docs",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SWAGGER_UI_DIST": "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.11.5",
}
