from django.db import models
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils.translation import gettext as _
from django.template.defaultfilters import slugify

import uuid
import os


def cover_image_filename(instance, filename):
    ext = os.path.splitext(filename)[-1]
    filename = "%s-cover%s" % (instance.slug, ext)
    return filename


# Create your models here.
class Podcast(models.Model):
    title = models.CharField(
        blank=False,
        null=False,
        max_length=255,
        verbose_name=_('Podcast Title'),
    )
    subtitle = models.CharField(
        blank=True,
        null=True,
        max_length=255,
        verbose_name=_('Podcast Subtitle'),
    )
    slug = models.SlugField(
        blank=True,
        null=False,
        unique=True,
        editable=False,
    )
    feed_url = models.URLField(
        blank=False,
        null=False,
        unique=True,
        verbose_name=_('Feed URL'),
    )

    # Fields extracted at feed refresh
    updated = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('Last Feed Update'),
    )
    author = models.CharField(
        blank=True,
        null=True,
        max_length=255,
        verbose_name=_('Podcast Author'),
    )

    language = models.CharField(
        blank=True,
        null=True,
        max_length=64,
        verbose_name=_('Main Language'),
    )
    link = models.URLField(
        blank=True,
        null=True,
        max_length=64,
        verbose_name=_('Podcast Link'),
    )
    image = models.ImageField(
        blank=True,
        null=True,
        upload_to=cover_image_filename,
        verbose_name=_('Cover Image'),
    )
    itunes_explicit = models.NullBooleanField(
        verbose_name=_('Explicit Tag'),
    )
    itunes_type = models.CharField(
        blank=True,
        null=True,
        max_length=64,
        verbose_name=_('iTunes Type'),
    )
    generator = models.CharField(
        blank=True,
        null=True,
        max_length=64,
        verbose_name=_('Feed Generator'),
    )
    summary = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Podcast Summary'),
    )

    class Meta:
        verbose_name = _('Podcast')
        verbose_name_plural = _('Podcasts')

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.title)

        super().save(*args, **kwargs)


class Episode(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    guid = models.CharField(
        unique=True,
        max_length=255,
        editable=False,
    )
    podcast = models.ForeignKey(
        Podcast,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name='episodes',
        verbose_name=_('Podcast'),
    )
    title = models.CharField(
        blank=True,
        null=True,
        verbose_name=_('Episode Title'),
        max_length=255,
    )
    subtitle = models.CharField(
        blank=True,
        null=True,
        max_length=255,
        verbose_name=_('Episode Subtitle'),
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Podcast Summary'),
    )
    link = models.URLField(
        blank=True,
        null=True,
        verbose_name=_('Episode Link'),
    )
    media_url = models.URLField(
        blank=True,
        null=True,
        verbose_name=_('Media URL'),
    )
    published = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('Published'),
    )
    download_count = models.PositiveIntegerField(
        blank=False,
        null=False,
        default=0,
        verbose_name=_('Download Count'),
    )

    class Meta:
        verbose_name = _('Episode')
        verbose_name_plural = _('Episodes')
