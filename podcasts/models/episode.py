from django.db import models
from django.utils.translation import gettext as _

import uuid

from podcasts.conf import *
from podcasts.models import BigPositiveIntegerField


class Episode(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    guid = models.CharField(
        blank=False,
        null=False,
        unique=True,
        max_length=255,
        editable=False,
        verbose_name=_('Episode GUID'),
    )
    podcast = models.ForeignKey(
        'podcasts.Podcast',
        blank=False,
        null=False,
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
        verbose_name=_('Episode Summary'),
    )
    link = models.URLField(
        blank=True,
        null=True,
        verbose_name=_('Episode Link'),
    )
    media_url = models.URLField(
        blank=True,
        null=True,
        editable=False,
        verbose_name=_('Media URL'),
    )
    published = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('Published'),
    )
    downloaded = models.DateTimeField(
        blank=True,
        null=True,
        default=None,
        verbose_name=_('Downloaded'),
    )

    # iTunes-secific attributes
    itunes_duration = models.CharField(
        blank=True,
        null=True,
        max_length=32,
        verbose_name=_('Duration'),
    )
    itunes_season = models.CharField(
        blank=True,
        null=True,
        max_length=32,
        verbose_name=_('Season'),
    )
    itunes_episode = models.CharField(
        blank=True,
        null=True,
        max_length=32,
        verbose_name=_('Episode Number'),
    )
    itunes_episodetype = models.CharField(
        blank=True,
        null=True,
        max_length=16,
        verbose_name=_('Episode Type'),
    )

    # Fields related to file storage
    file_originalname = models.CharField(
        blank=True,
        null=True,
        max_length=255,
        verbose_name=_('Original Filename'),
    )
    file_path = models.FilePathField(
        path=STORAGE_DIRECTORY,
        blank=True,
        null=True,
        recursive=True,
        allow_files=True,
        allow_folders=False,
        verbose_name=_('File Location'),
    )
    file_size = BigPositiveIntegerField(
        blank=True,
        null=True,
        verbose_name=_('File Size'),
    )
    file_sha256 = models.CharField(
        blank=True,
        null=True,
        verbose_name=_('File Hash (SHA256)'),
        max_length=64,
    )

    # Listeners and states
    listeners = models.ManyToManyField(
        'podcasts.Listener',
        through='EpisodePlaybackState',
        through_fields=('episode', 'listener'),
        verbose_name=_('Episodes\' Listeners'),
    )

    class Meta:
        verbose_name = _('Episode')
        verbose_name_plural = _('Episodes')

    def __str__(self):
        if self.title is not None:
            return self.title
        else:
            return "%(podcast)s's Episode" % {'podcast': self.podcast}

