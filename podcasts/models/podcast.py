import itertools
import logging
from urllib.parse import urlencode
from urllib.parse import urlparse
from urllib.parse import urlunparse

import requests
from actstream import action
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.db.transaction import atomic
from django.dispatch import receiver
from django.shortcuts import reverse
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.utils.translation import gettext as _

from podcasts.conf import DEFAULT_DATE_FORMAT
from podcasts.conf import DEFAULT_NAMING_SCHEME
from podcasts.conf import ITUNES_LOOKUP_URL
from podcasts.conf import STORAGE_DIRECTORY
from podcasts.models.common import CommonAbstract
from podcasts.models.episode import Episode
from podcasts.utils import feed_info
from podcasts.utils import HEADERS
from podcasts.utils import refresh_feed


logger = logging.getLogger(__name__)

User = get_user_model()


class PodcastManager(models.Manager):
    @atomic
    def create_from_feed_url(self, feed_url, **kwargs):
        feed_info = kwargs.pop("feed_info", None)
        if not feed_info:
            feed_info = refresh_feed(feed_url)
        if feed_info is None:
            logger.error("Feed %(feed)s seems dead" % {"feed": feed_url})
            return

        logger.info("Creating %(podcast)s" % {"podcast": feed_info.data["title"]})
        podcast = Podcast(feed_url=feed_info.url)
        podcast.update(feed_info=feed_info, create_episodes=False, **kwargs)
        podcast.queue_full_update()
        return podcast

    def get_or_create_from_feed_url(
        self, feed_url, feed_info=None, subscriber=None, **kwargs
    ):
        self._for_write = True
        if not feed_info:
            feed_info = refresh_feed(feed_url)
        if not feed_info:
            logger.error("Feed %(feed)s seems dead" % {"feed": feed_url})
            return None, False

        created = False
        try:
            podcast = self.get(feed_url=feed_info.url)
            logger.info("Found existing %(podcast)s" % {"podcast": podcast.title})
        except self.model.DoesNotExist:
            # Args now include feed_info to prevent a second refresh happening down the line
            podcast = self.create_from_feed_url(
                feed_info.url, feed_info=feed_info, **kwargs
            )
            created = True
        if subscriber:
            podcast.subscribers.add(subscriber)
        return podcast, created

    def create_from_itunes_id(self, itunes_id, **kwargs):
        url_parts = list(urlparse(ITUNES_LOOKUP_URL))
        url_parts[4] = urlencode({"id": itunes_id})
        url = urlunparse(url_parts)
        response = requests.get(url, headers=HEADERS)
        data = response.json()
        if "resultCount" in data and data["resultCount"] > 0:
            kwargs["itunes_id"] = itunes_id
            return self.create_from_feed_url(data["results"][0]["feedUrl"], **kwargs)

    def get_or_create_from_itunes_id(self, itunes_id, **kwargs):
        url_parts = list(urlparse(ITUNES_LOOKUP_URL))
        url_parts[4] = urlencode({"id": itunes_id})
        url = urlunparse(url_parts)
        response = requests.get(url, headers=HEADERS)
        data = response.json()

        if "resultCount" in data and data["resultCount"] > 0:
            return self.get_or_create_from_feed_url(
                data["results"][0]["feedUrl"], **kwargs
            )


class Podcast(CommonAbstract):
    title = models.CharField(
        default="Untitled", null=False, max_length=255, verbose_name=_("Podcast Title")
    )
    subtitle = models.CharField(
        blank=True, null=True, max_length=255, verbose_name=_("Podcast Subtitle")
    )
    slug = models.SlugField(blank=True, null=False, unique=True, editable=False)
    feed_url = models.URLField(
        blank=False,
        null=False,
        max_length=2048,
        unique=True,
        verbose_name=_("Feed URL"),
    )

    added = models.DateTimeField(auto_now_add=True, verbose_name=_("Podcast Added"))
    fetched = models.DateTimeField(
        blank=True, null=True, verbose_name=_("Feed Fetched Last")
    )
    # Fields extracted at feed refresh
    updated = models.DateTimeField(
        blank=True, null=True, verbose_name=_("Last Feed Update")
    )
    author = models.CharField(
        blank=True, null=True, max_length=255, verbose_name=_("Podcast Author")
    )

    language = models.CharField(
        blank=True, null=True, max_length=64, verbose_name=_("Main Language")
    )
    link = models.URLField(
        blank=True, null=True, max_length=2048, verbose_name=_("Podcast Link")
    )
    itunes_explicit = models.NullBooleanField(verbose_name=_("Explicit Tag"))
    itunes_type = models.CharField(
        blank=True, null=True, max_length=64, verbose_name=_("iTunes Type")
    )
    generator = models.CharField(
        blank=True, null=True, max_length=64, verbose_name=_("Feed Generator")
    )
    summary = models.TextField(blank=True, null=True, verbose_name=_("Podcast Summary"))

    objects = PodcastManager()

    subscribers = models.ManyToManyField(
        User, verbose_name=_("Subscribers"), related_name="subscribed_podcasts"
    )
    followers = models.ManyToManyField(
        User, verbose_name=_("Follwers"), related_name="interested_podcasts"
    )

    class Meta:
        verbose_name = _("Podcast")
        verbose_name_plural = _("Podcasts")
        db_table = "podcasts_podcast"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("podcasts:podcasts-details", kwargs={"slug": self.slug})

    @atomic
    def create_episodes(self, info_or_episodes=None):
        if info_or_episodes is None:
            feed_info_obj = refresh_feed(self.feed_url)
            episode_info = feed_info_obj.data["episodes"]
        elif isinstance(info_or_episodes, dict):
            episode_info = info_or_episodes["episodes"]
        elif isinstance(info_or_episodes, feed_info):
            episode_info = info_or_episodes.data["episodes"]
        else:
            episode_info = info_or_episodes

        all_created = []
        for ep in episode_info:
            ep["podcast"] = self
            image = ep.pop("image", None)

            episode, created = Episode.objects.update_or_create(
                guid=ep["guid"], defaults=ep
            )

            episode.insert_cover(image)
            all_created.append(created)

        return all_created

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
        return self.summary

    @property
    def num_episodes(self):
        return self.episodes.count()

    def last_published(self):
        return self.episodes.aggregate(last=models.Max("published"))["last"]

    def queue_full_update(self):
        from podcasts.tasks import refresh_feed

        refresh_feed(self.id)
        logger.info("Queued refresh task")

    def update(
        self,
        feed_info=None,
        create_episodes=True,
        insert_cover=True,
        update_all=False,
        only_first_page=False,
    ):
        if not feed_info:
            feed_info = refresh_feed(self.feed_url)

        defaults = feed_info.data
        defaults["feed_url"] = feed_info.url
        defaults["fetched"] = timezone.now()

        logger.info(
            "Fetched %(podcast)s at %(timestamp)s"
            % {"podcast": defaults["title"], "timestamp": defaults["fetched"]}
        )

        episodes = defaults.pop("episodes", None)
        image = defaults.pop("image", None)
        for key, value in defaults.items():
            setattr(self, key, value)

        if image is not None and insert_cover:
            logger.info("Inserting cover image")
            self.insert_cover(image)

        if create_episodes:
            logger.info("Inserting episodes from first page")
            all_created = self.create_episodes(info_or_episodes=episodes)

            # Continue while
            # * There is a next page
            # * Not only the first page should be processed
            # * All episodes are new OR existing episodes should be updated
            while (
                feed_info.next_page
                and not only_first_page
                and (False not in all_created or update_all)
            ):

                logger.info("Fetching next page %s ..." % feed_info.next_page)

                feed_info = refresh_feed(feed_info.next_page)
                episodes = feed_info.data.pop("episodes", None)
                all_created = self.create_episodes(info_or_episodes=episodes)

            if False in all_created:
                logger.info("Found existing episodes")
            if not feed_info.next_page:
                logger.info("No next page found")

        logger.info("All done")
        self.save()
        action.send(self, verb="was fetched", timestamp=defaults["fetched"])
        if self.updated:
            action.send(self, verb="was updated", timestamp=self.updated)

    @atomic
    def queue_missing_episodes_download_tasks(
        self,
        storage_directory=STORAGE_DIRECTORY,
        naming_scheme=DEFAULT_NAMING_SCHEME,
        inpath_dateformat=DEFAULT_DATE_FORMAT,
    ):
        for episode in self.episodes.filter(downloaded=None):
            episode.queue_download_task(
                storage_directory, naming_scheme, inpath_dateformat
            )


@receiver(post_save, sender=Podcast)
def log_activity(sender, instance, created, **kwargs):
    if created:
        action.send(instance, verb="was added")
