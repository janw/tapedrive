from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _

from podcasts.conf import *
from podcasts.models import IntegerRangeField
from podcasts.models.podcast import Podcast

User = get_user_model()


class Listener(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    subscribed_podcasts = models.ManyToManyField(
        'podcasts.Podcast',
        verbose_name=_('Subscribed Podcasts'),
        related_name='subscribers',
    )
    interested_podcasts = models.ManyToManyField(
        'podcasts.Podcast',
        verbose_name=_('Added Podcasts'),
        related_name='followers',
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
        return _("User %(user)s") % {'user': self.user.username}

    def has_played(self, episode):
        if not EpisodePlaybackState.objects.get(episode=episode, listener=self):
            return False

    def subscribe_to_podcast(self, podcast):
        self.subscribed_podcasts.add(podcast)
        self.save()

    def follow_podcast(self, podcast):
        self.followers.add(listener)
        self.save()


@receiver(post_save, sender=User)
def create_user_listener(sender, instance, created, **kwargs):
    if created:
        Listener.objects.create(user=instance)


class EpisodePlaybackState(models.Model):
    episode = models.ForeignKey(
        'podcasts.Episode',
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

