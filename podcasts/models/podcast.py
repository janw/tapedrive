from django.core.files import File
from django.db import models
from django.db.transaction import atomic
from django.utils import timezone
from django.utils.translation import gettext as _
from django.shortcuts import reverse
from django.template.defaultfilters import slugify

from urllib.parse import urlparse
import urllib
from PIL import Image
from io import BytesIO

from podcasts.conf import *
from podcasts.utils import refresh_feed
from podcasts.models import cover_image_filename
from podcasts.models.episode import Episode


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

    def remove_subscriber(self, listener):
        self.subscribers.remove(listener)
        self.save()

    def add_follower(self, listener):
        self.followers.add(listener)
        self.save()

    def remove_follower(self, listener):
        self.followers.remove(listener)
        self.save()

    @property
    def subtitle_is_summary(self, cutoff=10):
        return self.subtitle[cutoff:-cutoff] in self.summary

    @property
    def subtitle_is_title(self):
        return self.subtitle.strip() in self.title.strip()

    @property
    def summary_p(self):
        if not self.summary.startswith('<p>'):
            return '<p>' + self.summary + '</p>'
        return self.summary


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

        return info

    @atomic
    def queue_missing_episodes_download_tasks(self, storage_directory=STORAGE_DIRECTORY, naming_scheme=DEFAULT_NAMING_SCHEME):
        for episode in self.episodes.filter(downloaded=None):
            print(episode)
            episode.queue_download_task(storage_directory, naming_scheme)
