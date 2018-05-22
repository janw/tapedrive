from django.db import models
from django.db.models.signals import post_save
from django.db.transaction import atomic
from django.dispatch import receiver
from django.utils.translation import gettext as _
from django.template.defaultfilters import slugify, date as _date

import os
from string import Template
import itertools

from podcasts.conf import *
from podcasts.models import BigPositiveIntegerField
from podcasts.utils import strip_url, AVAILABLE_EPISODE_SEGMENTS, AVAILABLE_PODCAST_SEGMENTS

from actstream import action


class Episode(models.Model):
    guid = models.CharField(
        blank=False,
        null=False,
        unique=True,
        max_length=255,
        editable=False,
        verbose_name=_('Episode GUID'),
    )
    slug = models.SlugField(
        blank=False,
        null=False,
        editable=False,
        max_length=255,
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

    download_task = models.OneToOneField(
        'background_task.Task',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_('Associated Download Task'),
    )

    class Meta:
        verbose_name = _('Episode')
        verbose_name_plural = _('Episodes')

    def __str__(self):
        if self.title is not None:
            return self.title
        else:
            return "%(podcast)s's Episode" % {'podcast': self.podcast}

    def save(self, *args, **kwargs):
        if not self.id or not self.slug:
            max_length = self._meta.get_field('slug').max_length
            self.slug = orig = slugify(self.title)
            for x in itertools.count(1):
                if not Episode.objects.filter(slug=self.slug).exists():
                    break
                self.slug = "%s-%d" % (orig[:max_length - len(str(x)) - 1], x)

        super().save(*args, **kwargs)

    def construct_file_path(self,
                            storage_directory=STORAGE_DIRECTORY,
                            naming_scheme=DEFAULT_NAMING_SCHEME,
                            inpath_dateformat=DEFAULT_DATE_FORMAT):
        linkpath, extension = strip_url(self.media_url)

        info = {}
        for key, value in AVAILABLE_EPISODE_SEGMENTS.items():
            info[key] = getattr(self, value, '')

            if key == 'episode_id':
                info[key] = str(info[key])
            elif key == 'podcast_updated' or key.endswith('_date'):
                info[key] = _date(info[key], inpath_dateformat)
            if info[key] is None:
                info[key] = ''

        for key, value in AVAILABLE_PODCAST_SEGMENTS.items():
            info[key] = getattr(self.podcast, value, '')

            if info[key] is None:
                info[key] = ''

        filename = Template(naming_scheme)
        filename = filename.safe_substitute(info)

        self.file_path = os.path.join(storage_directory, filename + extension)
        self.save()
        return self.file_path

    @atomic
    def queue_download_task(self,
                            storage_directory=STORAGE_DIRECTORY,
                            naming_scheme=DEFAULT_NAMING_SCHEME,
                            inpath_dateformat=DEFAULT_DATE_FORMAT,
                            overwrite=False):
        from podcasts.tasks import download_episode # noqa

        self.construct_file_path(storage_directory, naming_scheme, inpath_dateformat)
        if not os.path.isfile(self.file_path) or overwrite:
            self.download_task = download_episode(self.media_url, self.file_path, str(self.id))
            self.save()


@receiver(post_save, sender=Episode)
def log_activity(sender, instance, created, **kwargs):
    if created:
        action.send(instance, verb='was fetched from', target=instance.podcast)
        action.send(instance, verb='was published to', target=instance.podcast, timestamp=instance.published)
