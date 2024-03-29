import os

from django.db import models
from django.utils.translation import gettext as _

from podcasts.conf import DEFAULT_DATE_FORMAT, DEFAULT_NAMING_SCHEME, STORAGE_DIRECTORY
from podcasts.validators import validate_naming_scheme, validate_path


class IntegerRangeField(models.IntegerField):
    def __init__(self, verbose_name=None, name=None, min_value=None, max_value=None, **kwargs):
        self.min_value, self.max_value = min_value, max_value
        models.IntegerField.__init__(self, verbose_name, name, **kwargs)

    def formfield(self, **kwargs):
        defaults = {"min_value": self.min_value, "max_value": self.max_value}
        defaults.update(kwargs)
        return super().formfield(**defaults)


class PodcastsSettings(models.Model):
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
        help_text=_("Scheme used to compile date segments in episode download filenames"),
    )

    class Meta:
        verbose_name = _("Podcasts Settings")
        verbose_name_plural = _("Podcasts Settings")

    def __str__(self):
        return "Tape Drive Settings"

    def save(self, *args, **kwargs):
        # Expand user and vars now once, to prevent future changes to cause unexpected directory changes
        self.storage_directory = os.path.expanduser(os.path.expandvars(self.storage_directory))

        super().save(*args, **kwargs)
