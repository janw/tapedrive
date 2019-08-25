from django.apps import AppConfig
from django.apps import apps as global_apps
from django.db import DEFAULT_DB_ALIAS, router
from django.db.models.signals import post_migrate
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.utils import timezone

import logging

logger = logging.getLogger(__name__)


def create_background_refresh_task(
    app_config,
    verbosity=2,
    interactive=True,
    using=DEFAULT_DB_ALIAS,
    apps=global_apps,
    **kwargs,
):
    task_name = "podcasts.tasks.regular_feed_refresh"

    try:
        Task = apps.get_model("background_task", "Task")
    except LookupError:
        return

    if not router.allow_migrate_model(using, Task):
        return

    tasks = Task.objects.using(using).filter(task_name=task_name)
    if not tasks.exists():
        from podcasts.conf import (
            DEFAULT_REFRESH_RATE,
            DEFAULT_REFRESH_PRIORITY,
            DEFAULT_REFRESH_DELAY,
        )
        from podcasts.tasks import regular_feed_refresh

        task = regular_feed_refresh(
            repeat=DEFAULT_REFRESH_RATE,
            priority=DEFAULT_REFRESH_PRIORITY,
            schedule=DEFAULT_REFRESH_DELAY,
        )
        logger.info("Created feed refresh task")
    else:
        task = tasks[0]
        logger.info("Found existing feed refresh task")
    logger.info(
        "Is scheduled for %s" % timezone.get_current_timezone().normalize(task.run_at)
    )


# Shamelessly stolen and adapted from django.contrib.sites
def create_default_settings(
    app_config,
    verbosity=2,
    interactive=True,
    using=DEFAULT_DB_ALIAS,
    apps=global_apps,
    **kwargs,
):
    try:
        PodcastsSettings = apps.get_model("podcasts", "PodcastsSettings")
    except LookupError:
        return

    if not router.allow_migrate_model(using, PodcastsSettings):
        return

    if not PodcastsSettings.objects.using(using).exists():
        # The default settings set SITE_ID = 1 for django.contrib.sites, so we make
        # dependency on the default Site to create the initial settings object.
        if verbosity >= 2:
            print("Creating default PodcastsSettings")
        PodcastsSettings().save(using=using)


class PodcastsConfig(AppConfig):
    name = "podcasts"
    verbose_name = _("Podcasts")
    verbose_name_plural = _("Podcasts")

    def ready(self):
        post_migrate.connect(create_default_settings, sender=self)
        post_migrate.connect(create_background_refresh_task, sender=self)

        from actstream import registry  # noqa

        registry.register(self.get_model("Podcast"), self.get_model("Episode"))
