"""
Django settings for podcastarchive project.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""
from django.utils.translation import gettext_lazy as _

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


class DatabaseURLValueWithOptions(values.DatabaseURLValue):
    options_mysql = {"charset": "utf8mb4"}
    options_sqlite = {"timeout": 20}

    def to_python(self, value):
        value = super().to_python(value)
        if (
            value[self.alias]["ENGINE"] == "django.db.backends.mysql"
            and self.options_mysql is not None
        ):
            value[self.alias].update({"OPTIONS": self.options_mysql})
        if (
            value[self.alias]["ENGINE"] == "django.db.backends.sqlite"
            and self.options_sqlite is not None
        ):
            value[self.alias].update({"OPTIONS": self.options_sqlite})
        return value


class Common(Configuration):
    # Build paths inside the project like this: os.path.join(BASE_DIR, ...)
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))

    # SECURITY WARNING: keep the secret key used in production secret!
    SECRET_KEY = get_secret_key(BASE_DIR)

    # SECURITY WARNING: don't run with debug turned on in production!
    DEBUG = values.BooleanValue(False)
    DEBUG_FRONTEND = values.BooleanValue(False)

    ALLOWED_HOSTS = values.ListValue([], environ=True)

    # Application definition
    INSTALLED_APPS = [
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.humanize",
        "django.contrib.sites",
        # "whitenoise.runserver_nostatic",
        "django.contrib.staticfiles",
        "bootstrap4",
        "podcastarchive.users",
        "podcasts",
        "background_task",
        "actstream",
        "rest_framework",
    ]

    MIDDLEWARE = [
        "django.middleware.security.SecurityMiddleware",
        # "whitenoise.middleware.WhiteNoiseMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.middleware.locale.LocaleMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.contrib.sites.middleware.CurrentSiteMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
        # "podcastarchive.users.middleware.LoginRequiredMiddleware",
    ]

    ROOT_URLCONF = "podcastarchive.urls"

    TEMPLATES = [
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [os.path.join(BASE_DIR, "templates")],
            "APP_DIRS": True,
            "OPTIONS": {
                "context_processors": [
                    "django.template.context_processors.debug",
                    "django.template.context_processors.request",
                    "django.contrib.auth.context_processors.auth",
                    "django.contrib.messages.context_processors.messages",
                    "podcastarchive.context_processors.debug",
                ]
            },
        }
    ]

    WSGI_APPLICATION = "podcastarchive.wsgi.application"

    # Database
    # https://docs.djangoproject.com/en/2.0/ref/settings/#databases
    DATABASES = DatabaseURLValueWithOptions(
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

    # LOGIN_URL = "/login/"
    # LOGOUT_URL = "/logout/"
    # LOGIN_REDIRECT_URL = "podcasts:podcasts-list"
    # LOGIN_EXEMPT_URLS = ["admin/", "password/reset/", "static/"]

    SITE_ID = 1
    SITE_NAME = "Tape Drive"

    # Internationalization
    # https://docs.djangoproject.com/en/2.0/topics/i18n/
    LANGUAGE_CODE = "en-us"

    TIME_ZONE = "Europe/Berlin"

    USE_I18N = True

    USE_L10N = True

    USE_TZ = True

    LANGUAGES = [("de", _("German")), ("en", _("English"))]

    LOCALE_PATHS = (os.path.join(BASE_DIR, "locale"),)

    # Static files (CSS, JavaScript, Images)
    # https://docs.djangoproject.com/en/2.0/howto/static-files/
    STATIC_URL = "/static/"
    STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
    STATICFILES_FINDERS = [
        "django.contrib.staticfiles.finders.FileSystemFinder",
        "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    ]
    STATICFILES_DIRS = [os.path.join(BASE_DIR, "assets")]
    WHITENOISE_AUTOREFRESH = True
    WHITENOISE_USE_FINDERS = True

    MEDIA_URL = "/media/"
    MEDIA_ROOT = os.path.join(BASE_DIR, "mediafiles")

    AUTH_USER_MODEL = "users.User"

    DEBUG_TOOLBAR_CONFIG = {"JQUERY_URL": ""}

    # Project settings
    COVER_IMAGE_SIZE = (500, 500)

    MESSAGE_TAGS = {
        10: "alert-dark",
        20: "alert-info",
        25: "alert-success",
        30: "alert-warning",
        40: "alert-danger",
    }

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
        "DEFAULT_AUTHENTICATION_CLASSES": (
            "rest_framework.authentication.SessionAuthentication",
            "rest_framework_simplejwt.authentication.JWTAuthentication",
        )
    }


class Development(Common):
    """
    The in-development settings and the default configuration.
    """

    DEBUG = True
    DEBUG_FRONTEND = True

    INTERNAL_IPS = ["127.0.0.1"]

    INSTALLED_APPS = (
        ["livereload"] + Common.INSTALLED_APPS + ["django_extensions", "debug_toolbar"]
    )

    DATABASES = DatabaseURLValueWithOptions(
        "sqlite:///{}".format(os.path.join(Common.BASE_DIR, "db.sqlite3"))
    )

    MIDDLEWARE = Common.MIDDLEWARE + [
        "debug_toolbar.middleware.DebugToolbarMiddleware",
        "livereload.middleware.LiveReloadScript",
    ]

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

    with TemporaryDirectory() as tmpdirname:
        DATABASES = DatabaseURLValueWithOptions(
            "sqlite:///{}".format(os.path.join(tmpdirname, "tapedrive-testing.sqlite3"))
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
