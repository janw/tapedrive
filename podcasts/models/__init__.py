from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.sites.models import Site
from django.utils.translation import gettext as _

import os

from podcasts.conf import STORAGE_DIRECTORY, DEFAULT_NAMING_SCHEME, DEFAULT_DATE_FORMAT
from podcasts.validators import validate_path, validate_naming_scheme

from podcasts.models.episode_chapter import *  # noqa


def cover_image_filename(instance, filename):
    ext = os.path.splitext(filename)[-1]
    filename = "%s-cover%s" % (instance.slug, ext)
    return filename


class IntegerRangeField(models.IntegerField):
    def __init__(
        self, verbose_name=None, name=None, min_value=None, max_value=None, **kwargs
    ):
        self.min_value, self.max_value = min_value, max_value
        models.IntegerField.__init__(self, verbose_name, name, **kwargs)

    def formfield(self, **kwargs):
        defaults = {"min_value": self.min_value, "max_value": self.max_value}
        defaults.update(kwargs)
        return super().formfield(**defaults)


class BigPositiveIntegerField(models.PositiveIntegerField):
    def db_type(self, connection):
        return "bigint unsigned"


class PodcastsSettings(models.Model):
    site = models.OneToOneField(Site, on_delete=models.CASCADE)
    storage_directory = models.CharField(
        null=False,
        blank=False,
        max_length=255,
        default=STORAGE_DIRECTORY,
        validators=[validate_path],
        verbose_name=_("Storage Directory"),
        help_text=_("Root directory of where the podcast episodes are downloaded to"),
    )
    naming_scheme = models.CharField(
        null=False,
        blank=False,
        max_length=255,
        default=DEFAULT_NAMING_SCHEME,
        validators=[validate_naming_scheme],
        verbose_name=_("Episode Naming Scheme"),
        help_text=_("Scheme used to compile the episode download filenames"),
    )
    inpath_dateformat = models.CharField(
        null=False,
        blank=False,
        max_length=255,
        default=DEFAULT_DATE_FORMAT,
        validators=[],
        verbose_name=_("In-Path Date Format"),
        help_text=_(
            "Scheme used to compile date segments in episode download filenames"
        ),
    )

    class Meta:
        verbose_name = _("Podcasts Settings")
        verbose_name_plural = _("Podcasts Settings")

    def __str__(self):
        return "%s Podcasts Settings" % self.site.name

    def save(self, *args, **kwargs):
        # Expand user and vars now once, to prevent future changes to cause unexpected directory changes
        self.storage_directory = os.path.expanduser(
            os.path.expandvars(self.storage_directory)
        )

        super().save(*args, **kwargs)


@receiver(post_save, sender=Site)
def create_site_settings(sender, instance, created, **kwargs):
    if created:
        PodcastsSettings.objects.create(site=instance)
