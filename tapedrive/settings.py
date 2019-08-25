"""
Django settings for tapedrive project.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os
import random
from tempfile import TemporaryDirectory

from configurations import Configuration, values


def get_secret_key(PROJECT_DIR):
    SECRET_FILE = os.path.join(PROJECT_DIR, "secret.txt")
    try:
        with open(SECRET_FILE) as sf:
            SECRET_KEY = sf.read().strip()
    except IOError:
        try:
            SECRET_KEY = "".join(
                [
                    random.SystemRandom().choice(
                        "abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)"
                    )
                    for i in range(50)
                ]
            )
            with open(SECRET_FILE, "w") as sf:
                sf.write(SECRET_KEY)
        except IOError:
            Exception(
                "Please create a %s file with random characters \
            to generate your secret key!"
                % SECRET_FILE
            )
    return SECRET_KEY


class Common(Configuration):
    # Build paths inside the project like this: os.path.join(BASE_DIR, ...)
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))

    # SECURITY WARNING: keep the secret key used in production secret!
    SECRET_KEY = get_secret_key(BASE_DIR)

    # SECURITY WARNING: don't run with debug turned on in production!
    DEBUG = values.BooleanValue(False)

    ALLOWED_HOSTS = values.ListValue([], environ=True)

    # Application definition
    INSTALLED_APPS = [
        "whitenoise.runserver_nostatic",
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.messages",
        "django.contrib.sessions",
        "django.contrib.staticfiles",
        "listeners",
        "podcasts",
        "background_task",
        "actstream",
        "rest_framework",
    ]

    MIDDLEWARE = [
        "django.middleware.security.SecurityMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.common.CommonMiddleware",
        "whitenoise.middleware.WhiteNoiseMiddleware",
        "django.middleware.locale.LocaleMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
    ]

    ROOT_URLCONF = "tapedrive.urls"

    TEMPLATES = [
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [os.path.join(BASE_DIR, "frontend", "dist")],
            "APP_DIRS": True,
            "OPTIONS": {
                "context_processors": [
                    "django.template.context_processors.request",
                    "django.contrib.auth.context_processors.auth",
                    "django.contrib.messages.context_processors.messages",
                ]
            },
        }
    ]

    WSGI_APPLICATION = "tapedrive.wsgi.application"

    # Database
    # https://docs.djangoproject.com/en/2.0/ref/settings/#databases
    DATABASES = values.DatabaseURLValue(
        "postgres://tapedrive:tapedrive@localhost/tapedrive"
    )

    # Password validation
    # https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators
    AUTH_PASSWORD_VALIDATORS = [
        {
            "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
        },
        {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
        {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
        {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
    ]

    LOGIN_REDIRECT_URL = "api-root"

    # Internationalization
    # https://docs.djangoproject.com/en/2.0/topics/i18n/
    LANGUAGE_CODE = "en-us"
    TIME_ZONE = "Europe/Berlin"
    USE_TZ = True

    # Static files (CSS, JavaScript, Images)
    # https://docs.djangoproject.com/en/2.0/howto/static-files/
    STATIC_URL = "/static/"
    STATIC_ROOT = os.path.join(BASE_DIR, "frontend", "dist")
    STATICFILES_FINDERS = [
        "django.contrib.staticfiles.finders.FileSystemFinder",
        "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    ]

    MEDIA_URL = "/media/"
    MEDIA_ROOT = os.path.join(BASE_DIR, "media")

    AUTH_USER_MODEL = "listeners.User"

    # Project settings
    COVER_IMAGE_SIZE = (500, 500)

    ACTSTREAM_SETTINGS = {
        "FETCH_RELATIONS": True,
        "USE_PREFETCH": True,
        "GFK_FETCH_DEPTH": 2,
    }

    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {"console": {"class": "logging.StreamHandler"}},
        "loggers": {
            "django": {"handlers": ["console"], "level": "INFO"},
            "podcasts": {"handlers": ["console"], "level": "INFO"},
        },
    }

    REST_FRAMEWORK = {
        "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
        "DEFAULT_AUTHENTICATION_CLASSES": (
            "rest_framework.authentication.SessionAuthentication",
            "rest_framework_simplejwt.authentication.JWTAuthentication",
        ),
    }


class Development(Common):
    """
    The in-development settings and the default configuration.
    """

    DEBUG = True

    INTERNAL_IPS = ["127.0.0.1"]

    INSTALLED_APPS = Common.INSTALLED_APPS + ["django_extensions", "debug_toolbar"]

    MIDDLEWARE = Common.MIDDLEWARE + ["debug_toolbar.middleware.DebugToolbarMiddleware"]

    SHELL_PLUS_PRE_IMPORTS = [
        ("podcasts.conf", "*"),
        ("podcasts.utils", "*"),
        ("feedparser"),
    ]

    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {"console": {"class": "logging.StreamHandler"}},
        "loggers": {
            "django": {"handlers": ["console"], "level": "INFO"},
            "podcasts": {"handlers": ["console"], "level": "INFO"},
        },
    }


class Testing(Common):
    def __init__(self, *args, **kwargs):
        super().__init(*args, **kwargs)
        with TemporaryDirectory() as tmpdirname:
            self.DATABASES = values.DatabaseURLValue(
                "sqlite:///{}".format(
                    os.path.join(tmpdirname, "tapedrive-testing.sqlite3")
                )
            )


class Staging(Common):
    """
    The in-staging settings.
    """

    # Security
    STRONG_SECURITY = values.BooleanValue(False)
    if STRONG_SECURITY is True:
        SESSION_COOKIE_SECURE = values.BooleanValue(True)
        SECURE_HSTS_INCLUDE_SUBDOMAINS = values.BooleanValue(True)
        SECURE_HSTS_SECONDS = values.IntegerValue(31536000)

    SECURE_BROWSER_XSS_FILTER = values.BooleanValue(True)
    SECURE_CONTENT_TYPE_NOSNIFF = values.BooleanValue(True)
    SECURE_REDIRECT_EXEMPT = values.ListValue([])
    SECURE_SSL_HOST = values.Value(None)
    SECURE_PROXY_SSL_HEADER = values.TupleValue(("HTTP_X_FORWARDED_PROTO", "https"))


class Production(Staging):
    """
    The in-production settings.
    """

    pass
