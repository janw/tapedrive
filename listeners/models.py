from django.contrib.auth.models import AbstractUser
from django.db import models

from podcasts.enums import EpisodeOrder, ImageSecurityPolicy, PodcastOrder
from podcasts.models import IntegerRangeField


class User(AbstractUser):
    # How to display things in frontend
    PODCASTS_PER_PAGE = 15
    EPISODES_PER_PAGE = 30
    DEFAULT_PODCASTS_ORDER = "title"
    DEFAULT_EPISODES_ORDER = "-published"
    DEFAULT_IMAGE_SECURITY_POLICY = "f"
    SEEK_FORWARD_BY = 45
    SEEK_BACKWARD_BY = 30

    # Display settings
    sort_order_podcasts = models.CharField(
        choices=PodcastOrder,
        default=PodcastOrder.default(),
        max_length=3,
        verbose_name="Sort Podcasts By",
        help_text="Determines the sorting of podcasts in the podcasts list",
    )
    sort_order_episodes = models.CharField(
        choices=EpisodeOrder,
        default=EpisodeOrder.default(),
        max_length=4,
        verbose_name="Sort Episodes By",
        help_text="Determines the sorting of episodes on podcast detail pages",
    )
    dark_mode = models.BooleanField(
        default=False,
        verbose_name="Dark Mode",
        help_text="Reduce eye strain at night, increase awesomeness by day.",
    )
    image_security_policy = models.CharField(
        choices=ImageSecurityPolicy,
        default=ImageSecurityPolicy.default(),
        max_length=1,
        verbose_name="Image Security Policy",
        help_text="How to load external images in show notes, etc.",
    )

    # Settings for future playback functionality
    playback_seek_forward_by = IntegerRangeField(
        null=True,
        blank=True,
        default=SEEK_FORWARD_BY,
        min_value=1,
        max_value=360,
        verbose_name="Seek Duration Forward",
    )
    playback_seek_backward_by = IntegerRangeField(
        null=True,
        blank=True,
        default=SEEK_BACKWARD_BY,
        min_value=1,
        max_value=360,
        verbose_name="Seek Duration Backward",
    )

    def __str__(self):
        return f"User {self.username}"

    def has_played(self, episode):
        from podcasts.models.episode import EpisodePlaybackState

        if not EpisodePlaybackState.objects.get(episode=episode, listener=self):
            return False

    def subscribe_to_podcast(self, podcast):
        self.subscribed_podcasts.add(podcast)
        self.save()

    def follow_podcast(self, podcast):
        self.interested_podcasts.add(podcast)
        self.save()
