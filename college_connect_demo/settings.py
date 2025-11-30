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

# Add your Render app domain here
#ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'your-app.onrender.com']
ALLOWED_HOSTS = ['*']

CSRF_TRUSTED_ORIGINS = [
    'https://*.onrender.com',
    'http://localhost',
    'http://127.0.0.1',
]


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
    "whitenoise.middleware.WhiteNoiseMiddleware",  # <-- important for static files on Render
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
# DATABASE CONFIG
# ======================
DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
    )
}

# ======================
# STATIC & MEDIA FILES
# ======================
STATIC_URL = '/static/'

# Local static files folder
STATICFILES_DIRS = [BASE_DIR / "static"]

# Where collectstatic will put files
STATIC_ROOT = BASE_DIR / "staticfiles"

# Use Whitenoise Manifest storage for production (safe for Render)
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"


MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "mediafiles"

# ======================
# DEBUG SWITCH for STATICFILES_DIRS
# ======================
# If DEBUG=False on Render, keep STATICFILES_DIRS for collectstatic
# during build; it will be ignored in production after collectstatic
#if not DEBUG:
 #   STATICFILES_DIRS = [BASE_DIR / "static"]


# ======================
# SECURITY SETTINGS
# ======================
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
SECURE_SSL_REDIRECT = not DEBUG

# ======================
# EMAIL SETTINGS
# ======================
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config("EMAIL_USER")
EMAIL_HOST_PASSWORD = config("EMAIL_PASSWORD")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# ======================
# AUTH
# ======================
AUTH_USER_MODEL = "accounts.CustomUser"
AUTHENTICATION_BACKENDS = ["django.contrib.auth.backends.ModelBackend"]
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "login"

# ======================
# DEFAULT AUTO FIELD
# ======================
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
