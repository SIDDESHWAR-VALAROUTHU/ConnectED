import os
from pathlib import Path
from decouple import config
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# ======================
# SECURITY & KEYS
# ======================
SECRET_KEY = config("DJANGO_SECRET_KEY")
DEBUG = config("DEBUG", default="False").lower() == "true"
if not DEBUG:
    DEBUG_PROPAGATE_EXCEPTIONS = True


ALLOWED_HOSTS = ["*"]


# ======================
# INSTALLED APPS
# ======================
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "channels",
    "chat",
    "network",
    "jobs",
    "django.contrib.humanize",
    "accounts.apps.AccountsConfig",
]


# ======================
# MIDDLEWARE
# ======================
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


ROOT_URLCONF = "college_connect_demo.urls"

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
                "accounts.context_processors.pending_request_count",
            ],
        },
    },
]

WSGI_APPLICATION = "college_connect_demo.wsgi.application"
ASGI_APPLICATION = "college_connect_demo.asgi.application"


# ======================
# CHANNELS (safe fallback)
# ======================
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}


# ======================
# DATABASE CONFIG
# ======================
DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
    )
}


# ======================
# CUSTOM USER MODEL
# ======================
AUTH_USER_MODEL = "accounts.CustomUser"

AUTHENTICATION_BACKENDS = ["django.contrib.auth.backends.ModelBackend"]

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "login"


# ======================
# STATIC & MEDIA FILES
# ======================
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "mediafiles"

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"


# FIX: Remove STATICFILES_DIRS in Render Build (collectstatic)
if not DEBUG:
    STATICFILES_DIRS = []


# ======================
# SECURITY FOR RENDER
# ======================
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG

SECURE_SSL_REDIRECT = False  # free Render has SSL off on internal requests


# ======================
# EMAIL SETTINGS (Gmail)
# ======================
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config("EMAIL_USER")
EMAIL_HOST_PASSWORD = config("EMAIL_PASSWORD")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER


# ======================
# AUTO FIELD
# ======================
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"




import logging

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'ERROR',
    },
}
