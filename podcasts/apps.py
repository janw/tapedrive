from django.apps import AppConfig
from django.apps import apps as global_apps
from django.db import DEFAULT_DB_ALIAS, router
from django.db.models.signals import post_migrate
from django.utils.translation import gettext_lazy as _
from django.conf import settings


# Shamelessly stolen and adapted from django.contrib.sites
def create_default_settings(app_config, verbosity=2, interactive=True, using=DEFAULT_DB_ALIAS, apps=global_apps, **kwargs):
    try:
        Site = apps.get_model('sites', 'Site')
        PodcastsSettings = apps.get_model('podcasts', 'PodcastsSettings')
    except LookupError:
        return

    if not router.allow_migrate_model(using, PodcastsSettings):
        return

    if not PodcastsSettings.objects.using(using).exists():
        # The default settings set SITE_ID = 1 for django.contrib.sites, so we make
        # dependency on the default Site to create the initial settings object.
        site = Site.objects.get(pk=getattr(settings, 'SITE_ID', 1))
        if verbosity >= 2:
            print("Creating default PodcastsSettings, setting site name")
        site.name = getattr(settings, 'SITE_NAME', 'example.com')
        site.save(using=using)
        PodcastsSettings(site=site).save(using=using)


class PodcastsConfig(AppConfig):
    name = 'podcasts'
    verbose_name = _('Podcasts')
    verbose_name_plural = _('Podcasts')

    def ready(self):
        post_migrate.connect(create_default_settings, sender=self)
