"""
Django settings for SkillSwap AI project.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# -----------------------------------------------------------------------
# CORE / SECURITY
# -----------------------------------------------------------------------
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-CHANGE-THIS-IN-PRODUCTION-5%&11hys5xda1dezy",
)

DEBUG = os.environ.get("DJANGO_DEBUG", "True") == "True"

ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1,.onrender.com,*").split(",")

# -----------------------------------------------------------------------
# APPLICATIONS
# -----------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",

    # Third-party
    "crispy_forms",
    "crispy_bootstrap5",
    "channels",

    # Local apps
    "core.apps.CoreConfig",
    "accounts.apps.AccountsConfig",
    "profiles.apps.ProfilesConfig",
    "skills.apps.SkillsConfig",
    "matching.apps.MatchingConfig",
    "exchanges.apps.ExchangesConfig",
    "chatapp.apps.ChatappConfig",
    "dashboard.apps.DashboardConfig",
]


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

ROOT_URLCONF = "skillswap.urls"

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
                "core.context_processors.site_context",
            ],
        },
    },
]

# WSGI for normal HTTP, ASGI for Channels (chat over WebSockets)
WSGI_APPLICATION = "skillswap.wsgi.application"
ASGI_APPLICATION = "skillswap.asgi.application"

# -----------------------------------------------------------------------
# CHANNELS (Real-time chat)
# -----------------------------------------------------------------------
# Falls back to in-memory layer automatically if Redis isn't running yet,
# so `runserver` still works on day one. Switch to Redis for real
# multi-process / production use (set REDIS_URL).
REDIS_URL = os.environ.get("REDIS_URL")

if REDIS_URL:
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {"hosts": [REDIS_URL]},
        }
    }
else:
    CHANNEL_LAYERS = {
        "default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}
    }

import dj_database_url

DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            ssl_require=False,
        )
    }
elif os.environ.get("USE_POSTGRES", "False") == "True":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("DB_NAME", "skillswap"),
            "USER": os.environ.get("DB_USER", "skillswap_user"),
            "PASSWORD": os.environ.get("DB_PASSWORD", ""),
            "HOST": os.environ.get("DB_HOST", "localhost"),
            "PORT": os.environ.get("DB_PORT", "5432"),
        }
    }
else:
    if os.environ.get("VERCEL"):
        import shutil
        db_path = Path("/tmp/db.sqlite3")
        if not db_path.exists() and (BASE_DIR / "db.sqlite3").exists():
            try:
                shutil.copyfile(BASE_DIR / "db.sqlite3", db_path)
            except Exception:
                pass
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": db_path,
            }
        }
    else:
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": BASE_DIR / "db.sqlite3",
            }
        }

# -----------------------------------------------------------------------
# CUSTOM USER MODEL
# -----------------------------------------------------------------------
AUTH_USER_MODEL = "accounts.User"

AUTHENTICATION_BACKENDS = [
    "accounts.backends.EmailOrUsernameBackend",
    "django.contrib.auth.backends.ModelBackend",
]

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 8}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "dashboard:home"
LOGOUT_REDIRECT_URL = "core:landing"

# -----------------------------------------------------------------------
# CRISPY FORMS
# -----------------------------------------------------------------------
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# -----------------------------------------------------------------------
# I18N / TZ
# -----------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True

# -----------------------------------------------------------------------
# STATIC & MEDIA FILES
# -----------------------------------------------------------------------
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# -----------------------------------------------------------------------
# EMAIL (console backend for dev; switch to SMTP in production)
# -----------------------------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
EMAIL_BACKEND = os.environ.get(
    "EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend"
)
EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "SkillSwap AI <noreply@skillswap.ai>")

# -----------------------------------------------------------------------
# SECURITY (relaxed for DEBUG, tighten automatically in production)
# -----------------------------------------------------------------------
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    X_FRAME_OPTIONS = "DENY"

# Basic file upload limits (defense against abuse via profile pics/certs)
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024
