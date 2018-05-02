from django.db import models
from django.utils.translation import gettext as _
from django.template.defaultfilters import slugify

import uuid


# Create your models here.
class Podcast(models.Model):
    title = models.CharField(
        blank=False,
        null=False,
        max_length=255,
        verbose_name=_('Podcast Title'),
    )
    slug = models.SlugField(
        blank=True,
        null=False
    )
    feed_url = models.URLField(
        blank=False,
        null=False,
        verbose_name=_('Feed URL'),
    )
    feed_last_updated = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('Last Feed Update'),
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
    podcast = models.ForeignKey(
        Podcast,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name='episodes',
        verbose_name=_('Podcast'),
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
