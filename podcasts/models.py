from django.core.files import File
from django.db import models
from django.db.transaction import atomic
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _
from django.shortcuts import reverse
from django.template.defaultfilters import slugify

import uuid
import os
from urllib.parse import urlparse
import urllib
from PIL import Image
from io import BytesIO

from .conf import *
from .utils import refresh_feed, timeit

User = get_user_model()


def cover_image_filename(instance, filename):
    ext = os.path.splitext(filename)[-1]
    filename = "%s-cover%s" % (instance.slug, ext)
    return filename


class IntegerRangeField(models.IntegerField):
    def __init__(self, verbose_name=None, name=None, min_value=None, max_value=None, **kwargs):
        self.min_value, self.max_value = min_value, max_value
        models.IntegerField.__init__(self, verbose_name, name, **kwargs)

    def formfield(self, **kwargs):
        defaults = {'min_value': self.min_value, 'max_value': self.max_value}
        defaults.update(kwargs)
        return super().formfield(**defaults)


class BigPositiveIntegerField(models.PositiveIntegerField):
    def db_type(self, connection):
        return 'bigint unsigned'


# Create your models here.
class PodcastManager(models.Manager):

    @atomic
    def create_from_feed_url(self, feed_url, info=None):
        if info is None:
            info = refresh_feed(feed_url)

        episodes = info.pop('episodes', None)
        image = info.pop('image', None)
        podcast = self.create(feed_url=feed_url, **info)

        if image is not None:
            podcast.insert_cover(image)

        podcast.create_episodes(info_or_episodes=episodes, initial=True)
        return podcast

    def get_or_create_from_feed_url(self, feed_url, info=None, **kwargs):
        self._for_write = True
        try:
            return self.get(feed_url=feed_url), False
        except self.model.DoesNotExist:
            return self.create_from_feed_url(feed_url, info=info, **kwargs), True


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

    fetched = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('Feed Fetched Last'),
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

    objects = PodcastManager()

    class Meta:
        verbose_name = _('Podcast')
        verbose_name_plural = _('Podcasts')

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.title)

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('podcasts:podcasts-details', kwargs={'slug': self.slug})

    def create_episodes(self, info_or_episodes=None, initial=False):
        if info_or_episodes is None:
            episode_info = refresh_feed(self.feed_url)['episodes']
        elif isinstance(info_or_episodes, dict):
            episode_info = info_or_episodes['episodes']
        else:
            episode_info = info_or_episodes

        if initial:
            objects = (Episode(podcast=self, **ep) for ep in episode_info)
            Episode.objects.bulk_create(objects)
        else:
            for ep in episode_info:
                episode, created = Episode.objects.update_or_create(podcast=self, guid=ep['guid'], defaults=ep)

    def insert_cover(self, info_or_img_url=None):
        if info_or_img_url is None:
            img_url = refresh_feed(self.feed_url)['image']
        elif isinstance(info_or_img_url, dict):
            img_url = info_or_img_url['image']
        else:
            img_url = info_or_img_url

        name = urlparse(img_url).path.split('/')[-1]

        try:
            content, headers = urllib.request.urlretrieve(img_url)
            img_size = getattr(settings, 'COVER_IMAGE_SIZE', (250, 250))

            im = Image.open(content)
            output = BytesIO()

            # Resize the image (from https://djangosnippets.org/snippets/10597/)
            im.thumbnail(img_size)

            # After modifications, save it to the output
            im.save(output, format='JPEG', quality=95)
            output.seek(0)

            # See also: http://docs.djangoproject.com/en/dev/ref/files/file/
            self.image.save(name, File(output), save=True)

        except urllib.error.HTTPError as err:
            print('Oops', err.code)

        def add_subscriber(self, listener):
            self.subscribers.add(listener)
            self.save()

        def add_follower(self, listener):
            self.followers.add(listener)
            self.save()

    @atomic
    def update(self, defaults=None, create_episodes=True, insert_image=True):
        if defaults is None:
            defaults = refresh_feed(self.feed_url)
        info = defaults
        defaults['fetched'] = timezone.now()
        episodes = defaults.pop('episodes', None)
        image = defaults.pop('image', None)
        for key, value in defaults.items():
            setattr(self, key, value)

        if image is not None and insert_image:
            self.insert_cover(image)

        if create_episodes:
            self.create_episodes(info_or_episodes=episodes, initial=False)


class Listener(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    subscribed_podcasts = models.ManyToManyField(
        Podcast,
        verbose_name=_('User\'s Podcasts'),
    )

    # Settings for future playback functionality
    playback_seek_forward_by = IntegerRangeField(
        null=True,
        blank=True,
        default=SEEK_FORWARD_BY,
        min_value=1,
        max_value=360,
        verbose_name=_('Seek Duration Forward'),
    )
    playback_seek_backward_by = IntegerRangeField(
        null=True,
        blank=True,
        default=SEEK_BACKWARD_BY,
        min_value=1,
        max_value=360,
        verbose_name=_('Seek Duration Backward'),
    )

    def __str__(self):
        return _("Listener %(user)s") % {'user': self.user.username}

    def has_played(self, episode):
        if not EpisodePlaybackState.objects.get(episode=episode, listener=self):
            return False


class Episode(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    guid = models.CharField(
        unique=True,
        max_length=255,
        editable=False,
        verbose_name=_('Episode GUID'),
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
        Listener,
        through='EpisodePlaybackState',
        through_fields=('episode', 'listener'),
        verbose_name=_('Episodes\' Listeners'),
    )

    class Meta:
        verbose_name = _('Episode')
        verbose_name_plural = _('Episodes')

    def __str__(self):
        return self.title


class EpisodePlaybackState(models.Model):
    episode = models.ForeignKey(
        Episode,
        on_delete=models.CASCADE,
        related_name='playbackstates',
    )
    listener = models.ForeignKey(
        Listener,
        on_delete=models.CASCADE,
        related_name='playbackstates',
    )
    position = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Playback Position'),
    )
    completed = models.BooleanField(
        default=False,
        verbose_name=_('Playback Completed'),
    )

    def __str__(self):
        return "%(user)s's state on %(episode)s" % {'user': self.listener,
                                                    'episode': self.episode}
