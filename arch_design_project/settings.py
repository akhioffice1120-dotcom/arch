# arch_design_project/settings.py

from pathlib import Path
import os

from decouple import config
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent


# -------------------------------------------------
# Core
# -------------------------------------------------
SECRET_KEY = config("SECRET_KEY", default="unsafe-dev-secret-key")  # production এ অবশ্যই env এ দিবে
DEBUG = config("DEBUG", default=False, cast=bool)

# "localhost,127.0.0.1,example.com" -> ["localhost","127.0.0.1","example.com"]
ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    default="localhost,127.0.0.1"
).split(",")

# Remove whitespace just in case
ALLOWED_HOSTS = [h.strip() for h in ALLOWED_HOSTS if h.strip()]


# CSRF trusted origins (domain বসালে লাগবে)
# Example: "https://yourdomain.com,https://www.yourdomain.com"
_raw_csrf = config("CSRF_TRUSTED_ORIGINS", default="")
CSRF_TRUSTED_ORIGINS = [x.strip() for x in _raw_csrf.split(",") if x.strip()] if _raw_csrf else []


# -------------------------------------------------
# Apps
# -------------------------------------------------
INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third party
    "ckeditor",
    "ckeditor_uploader",
    "django_cleanup.apps.CleanupConfig",
    "widget_tweaks",
    "crispy_forms",
    "crispy_bootstrap5",

    # Local
    "arch_design.apps.ArchDesignConfig",
    "dashboard",
]


# -------------------------------------------------
# Middleware
# -------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # ✅ WhiteNoise add
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# -------------------------------------------------
# URLs / WSGI
# -------------------------------------------------
ROOT_URLCONF = "arch_design_project.urls"
WSGI_APPLICATION = "arch_design_project.wsgi.application"


# -------------------------------------------------
# Templates
# -------------------------------------------------
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
                "arch_design.context_processors.site_config",
            ],
        },
    },
]


# -------------------------------------------------
# Database (Render/Postgres via DATABASE_URL)
# -------------------------------------------------
DATABASES = {
    "default": dj_database_url.config(
        default=config("DATABASE_URL", default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}"),
        conn_max_age=600,
        ssl_require=config("DB_SSL_REQUIRE", default=False, cast=bool),
    )
}


# -------------------------------------------------
# Auth redirects
# -------------------------------------------------
LOGIN_URL = "dashboard_login"
LOGIN_REDIRECT_URL = "dashboard_home"
LOGOUT_REDIRECT_URL = "home"


# -------------------------------------------------
# Password validation
# -------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# -------------------------------------------------
# Internationalization
# -------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = config("TIME_ZONE", default="UTC")
USE_I18N = True
USE_TZ = True


# -------------------------------------------------
# Static / Media
# -------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# তোমার app static folder
STATICFILES_DIRS = [BASE_DIR / "arch_design" / "static"]

# WhiteNoise optimized static
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# MEDIA_URL = "/media/"
# MEDIA_ROOT = BASE_DIR / "media"


# -------------------------------------------------
# CKEditor
# -------------------------------------------------
CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_CONFIGS = {
    "default": {
        "toolbar": "full",
        "height": 300,
        "width": "100%",
    }
}

# IMPORTANT NOTE:
# Render free web service এ MEDIA (uploads) স্থায়ী থাকে না (restart হলে হারাতে পারে)
# Best: S3/Cloudinary/R2 ব্যবহার করা।


# -------------------------------------------------
# Crispy Forms
# -------------------------------------------------
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"


# -------------------------------------------------
# Email
# -------------------------------------------------
EMAIL_BACKEND = config(
    "EMAIL_BACKEND",
    default="django.core.mail.backends.console.EmailBackend"
)
EMAIL_HOST = config("EMAIL_HOST", default="")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="noreply@archdesign.com")


# -------------------------------------------------
# Security (Production best practice)
# Enable these when you're on HTTPS
# -------------------------------------------------
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Set this TRUE if you are serving via HTTPS (Render custom domain / reverse proxy https)
USE_HTTPS = config("USE_HTTPS", default=False, cast=bool)

SESSION_COOKIE_SECURE = USE_HTTPS
CSRF_COOKIE_SECURE = USE_HTTPS

# Helps mitigate XSS/Clickjacking
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# If HTTPS, good to redirect all http -> https
SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=False, cast=bool) if USE_HTTPS else False

# HSTS (only enable after confirming HTTPS works perfectly)
SECURE_HSTS_SECONDS = config("SECURE_HSTS_SECONDS", default=0, cast=int) if USE_HTTPS else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = config("SECURE_HSTS_INCLUDE_SUBDOMAINS", default=False, cast=bool) if USE_HTTPS else False
SECURE_HSTS_PRELOAD = config("SECURE_HSTS_PRELOAD", default=False, cast=bool) if USE_HTTPS else False


# -------------------------------------------------
# Default primary key field type
# -------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# -------------------------------------------------
# Optional: Basic logging (helpful in production)
# -------------------------------------------------
LOG_LEVEL = config("LOG_LEVEL", default="INFO")
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "root": {
        "handlers": ["console"],
        "level": LOG_LEVEL,
    },
}

# ---- Media storage (Cloudinary) ----
INSTALLED_APPS += ["cloudinary", "cloudinary_storage"]

CLOUDINARY_STORAGE = {
    "CLOUD_NAME": config("CLOUDINARY_CLOUD_NAME"),
    "API_KEY": config("CLOUDINARY_API_KEY"),
    "API_SECRET": config("CLOUDINARY_API_SECRET"),
}

DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"

# MEDIA_URL = "/media/"
