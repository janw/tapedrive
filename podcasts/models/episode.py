from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.db.transaction import atomic
from django.dispatch import receiver
from django.utils.translation import gettext as _
from django.template.defaultfilters import slugify, date as _date

import os
from uuid import uuid4
from string import Template
import itertools

from podcasts.conf import STORAGE_DIRECTORY, DEFAULT_NAMING_SCHEME, DEFAULT_DATE_FORMAT
from podcasts.utils import strip_url
from podcasts.utils.properties import (
    AVAILABLE_EPISODE_SEGMENTS,
    AVAILABLE_PODCAST_SEGMENTS,
)
from podcasts.models.common import CommonAbstract
from podcasts import utils
from actstream import action


class Episode(CommonAbstract):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    guid = models.CharField(
        blank=False,
        null=False,
        unique=True,
        max_length=255,
        editable=False,
        verbose_name=_("Episode GUID"),
    )
    slug = models.SlugField(blank=False, null=False, editable=False, max_length=255)
    podcast = models.ForeignKey(
        "podcasts.Podcast",
        blank=False,
        null=False,
        on_delete=models.CASCADE,
        related_name="episodes",
        verbose_name=_("Podcast"),
    )
    title = models.CharField(
        blank=True, null=True, verbose_name=_("Episode Title"), max_length=255
    )
    subtitle = models.CharField(
        blank=True, null=True, max_length=255, verbose_name=_("Episode Subtitle")
    )
    description = models.TextField(
        blank=True, null=True, verbose_name=_("Episode Summary")
    )
    link = models.URLField(blank=True, null=True, verbose_name=_("Episode Link"))
    media_url = models.URLField(
        blank=True,
        null=True,
        editable=False,
        verbose_name=_("Media URL"),
        max_length=2047,
    )
    published = models.DateTimeField(blank=True, null=True, verbose_name=_("Published"))
    downloaded = models.DateTimeField(
        blank=True, null=True, default=None, verbose_name=_("Downloaded")
    )

    # iTunes-secific attributes
    itunes_duration = models.CharField(
        blank=True, null=True, max_length=32, verbose_name=_("Duration")
    )
    itunes_season = models.CharField(
        blank=True, null=True, max_length=32, verbose_name=_("Season")
    )
    itunes_episode = models.CharField(
        blank=True, null=True, max_length=32, verbose_name=_("Episode Number")
    )
    itunes_episodetype = models.CharField(
        blank=True, null=True, max_length=16, verbose_name=_("Episode Type")
    )

    # Fields related to file storage
    file_originalname = models.CharField(
        blank=True, null=True, max_length=255, verbose_name=_("Original Filename")
    )
    file_path = models.FilePathField(
        path=STORAGE_DIRECTORY,
        blank=True,
        null=True,
        recursive=True,
        allow_files=True,
        allow_folders=False,
        verbose_name=_("File Location"),
    )
    file_size = models.BigIntegerField(
        blank=True, null=True, verbose_name=_("File Size")
    )
    file_sha256 = models.CharField(
        blank=True, null=True, verbose_name=_("File Hash (SHA256)"), max_length=64
    )

    # Listeners and states
    user = models.ManyToManyField(
        get_user_model(),
        through="EpisodePlaybackState",
        through_fields=("episode", "user"),
        verbose_name=_("Episodes' Listeners"),
    )

    download_task = models.OneToOneField(
        "background_task.Task",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Associated Download Task"),
    )

    shownotes = models.TextField(blank=True, null=True, verbose_name=_("Show Notes"))

    class Meta:
        verbose_name = _("Episode")
        verbose_name_plural = _("Episodes")
        db_table = "podcasts_episode"

    def __str__(self):
        if self.title is not None:
            return self.title
        else:
            return "%(podcast)s's Episode" % {"podcast": self.podcast}

    def save(self, *args, **kwargs):
        if not self.id or not self.slug:
            max_length = self._meta.get_field("slug").max_length
            self.slug = orig = slugify(self.title)
            for x in itertools.count(1):
                if not Episode.objects.filter(slug=self.slug).exists():
                    break
                self.slug = "%s-%d" % (orig[: max_length - len(str(x)) - 1], x)

            # Some episodes have ridiculously long titles
            if len(self.slug) > max_length:
                self.slug = self.slug[:max_length]
            if self.slug.endswith("-"):
                self.slug = self.slug[:-1]

        super().save(*args, **kwargs)

    def get_content(self, allowed_domains=False):
        if self.shownotes:
            return utils.replace_shownotes_images(self.shownotes, allowed_domains)
        else:
            return self.description

    def construct_file_path(
        self,
        storage_directory=STORAGE_DIRECTORY,
        naming_scheme=DEFAULT_NAMING_SCHEME,
        inpath_dateformat=DEFAULT_DATE_FORMAT,
    ):
        linkpath, extension = strip_url(self.media_url)

        info = {}
        for key, value in AVAILABLE_EPISODE_SEGMENTS.items():
            info[key] = getattr(self, value, "")

            if key == "episode_id":
                info[key] = str(info[key])
            elif key == "podcast_updated" or key.endswith("_date"):
                info[key] = _date(info[key], inpath_dateformat)
            if info[key] is None:
                info[key] = ""

        for key, value in AVAILABLE_PODCAST_SEGMENTS.items():
            info[key] = getattr(self.podcast, value, "")

            if info[key] is None:
                info[key] = ""

        filename = Template(naming_scheme)
        filename = filename.safe_substitute(info)

        self.file_path = os.path.join(storage_directory, filename + extension)
        self.save()
        return self.file_path

    @atomic
    def queue_download_task(
        self,
        storage_directory=STORAGE_DIRECTORY,
        naming_scheme=DEFAULT_NAMING_SCHEME,
        inpath_dateformat=DEFAULT_DATE_FORMAT,
        overwrite=False,
    ):
        from podcasts.tasks import download_episode  # noqa

        self.construct_file_path(storage_directory, naming_scheme, inpath_dateformat)
        if not os.path.isfile(self.file_path) or overwrite:
            self.download_task = download_episode(
                self.media_url, self.file_path, str(self.id)
            )
            self.save()

    def add_chapters(self, chapters):
        for chap in chapters:
            object, created = self.chapters.update_or_create(**chap)

    def get_chapters(self):
        if self.chapters.exists():
            return self.chapters.all()


@receiver(post_save, sender=Episode)
def log_activity(sender, instance, created, **kwargs):
    if created:
        action.send(instance, verb="was fetched from", target=instance.podcast)
        if instance.published:
            action.send(
                instance,
                verb="was published to",
                target=instance.podcast,
                timestamp=instance.published,
            )


class EpisodePlaybackState(models.Model):
    episode = models.ForeignKey(
        "podcasts.Episode", on_delete=models.CASCADE, related_name="playbackstates"
    )
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="playbackstates"
    )
    position = models.PositiveIntegerField(
        default=0, verbose_name=_("Playback Position")
    )
    completed = models.BooleanField(default=False, verbose_name=_("Playback Completed"))

    def __str__(self):
        return "%(user)s's state on %(episode)s" % {
            "user": self.listener,
            "episode": self.episode,
        }
