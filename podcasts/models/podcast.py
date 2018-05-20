from django.core.files import File
from django.db import models
from django.db.transaction import atomic
from django.utils import timezone
from django.utils.translation import gettext as _
from django.shortcuts import reverse
from django.template.defaultfilters import slugify

from io import BytesIO
import itertools
import logging

from podcasts.conf import *
from podcasts.utils import refresh_feed, feed_info, download_cover
from podcasts.models import cover_image_filename
from podcasts.models.episode import Episode


logger = logging.getLogger(__name__)


class PodcastManager(models.Manager):

    @atomic
    def create_from_feed_url(self, feed_url, **kwargs):
        feed_info = kwargs.pop('feed_info', None)
        if not feed_info:
            feed_info = refresh_feed(feed_url)
        if feed_info is None:
            return

        podcast = Podcast(feed_url=feed_info.url)
        return podcast.update(feed_info=feed_info, **kwargs)

    def get_or_create_from_feed_url(self, feed_url, **kwargs):
        self._for_write = True
        feed_info = kwargs.pop('feed_info', None)
        if not feed_info:
            feed_info = refresh_feed(feed_url)

        try:
            return self.get(feed_url=feed_info.url), False
        except self.model.DoesNotExist:
            # Args now include feed_info to prevent a second refresh happening down the line
            return self.create_from_feed_url(feed_info.url, feed_info=feed_info, **kwargs), True


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
        if not self.id or not self.slug:
            max_length = self._meta.get_field('slug').max_length
            self.slug = orig = slugify(self.title)
            for x in itertools.count(1):
                if not Podcast.objects.filter(slug=self.slug).exists():
                    break
                self.slug = "%s-%d" % (orig[:max_length - len(str(x)) - 1], x)

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('podcasts:podcasts-details', kwargs={'slug': self.slug})

    @atomic
    def create_episodes(self, info_or_episodes=None):
        if info_or_episodes is None:
            feed_info_obj = refresh_feed(self.feed_url)
            episode_info = feed_info_obj.data['episodes']
        elif isinstance(info_or_episodes, dict):
            episode_info = info_or_episodes['episodes']
        elif isinstance(info_or_episodes, feed_info):
            episode_info = info_or_episodes.data['episodes']
        else:
            episode_info = info_or_episodes

        all_created = []
        for ep in episode_info:
            ep['podcast'] = self
            episode, created = Episode.objects.update_or_create(guid=ep['guid'], defaults=ep)
            all_created.append(created)
        return all_created

    def insert_cover(self, img_url):
        output = BytesIO()
        name = download_cover(img_url, output)

        if name:
            self.image.save(name, File(output), save=True)

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
    def update(self, feed_info=None, create_episodes=True, insert_cover=True, update_all=False):
        if not feed_info:
            feed_info = refresh_feed(self.feed_url)

        defaults = feed_info.data
        defaults['feed_url'] = feed_info.url
        defaults['fetched'] = timezone.now()

        logger.info('Fetched %(podcast)s at %(timestamp)s' % {
            'podcast': defaults['title'], 'timestamp': defaults['fetched']})

        episodes = defaults.pop('episodes', None)
        image = defaults.pop('image', None)
        for key, value in defaults.items():
            setattr(self, key, value)

        if image is not None and insert_cover:
            logger.info('Inserting cover image')
            self.insert_cover(image)

        if create_episodes:
            logger.info('Inserting episodes from first page')
            all_created = self.create_episodes(info_or_episodes=episodes)

            # Parse pages of paginated feed
            while feed_info.next_page and (False not in all_created or update_all):
                logger.info('Fetching next page %s ...' % feed_info.next_page)

                feed_info = refresh_feed(feed_info.next_page)
                episodes = feed_info.data.pop('episodes', None)
                all_created = self.create_episodes(info_or_episodes=episodes)

            if False in all_created:
                logger.info('Found existing episodes')
            if not feed_info.next_page:
                logger.info('No next page found')

        logger.info('All done')
        self.save()
        return self

    @atomic
    def queue_missing_episodes_download_tasks(self,
                                              storage_directory=STORAGE_DIRECTORY,
                                              naming_scheme=DEFAULT_NAMING_SCHEME,
                                              inpath_dateformat=DEFAULT_DATE_FORMAT):
        for episode in self.episodes.filter(downloaded=None):
            episode.queue_download_task(storage_directory, naming_scheme, inpath_dateformat)
