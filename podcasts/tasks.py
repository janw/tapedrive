import logging

from django.contrib.auth import get_user_model
from django.utils import timezone

from podcasts.models import PodcastsSettings
from podcasts.models.episode import Episode
from podcasts.models.podcast import Podcast
from podcasts.utils import download_file

from background_task import background
from actstream import action

User = get_user_model()

logger = logging.getLogger(__name__)


@background()
def download_episode(media_url, file_path, id):

    # Get Episode from database
    episode = Episode.objects.get(id=id)
    print("Downloading episode %s ..." % episode)

    # Download the file
    filesize = download_file(media_url, file_path)

    if filesize:
        # Update Episode after download
        episode.file_size = filesize
        episode.downloaded = timezone.now()
        episode.save()
        action.send(episode, verb="was downloaded")
    else:
        action.send(episode, verb="failed downloading")


@background()
def regular_feed_refresh():
    for psettings in PodcastsSettings.objects.iterator():

        print("Queueing feed refreshes ...")
        # Refresh feeds of podcasts with at least one follower
        for podcast in Podcast.objects.filter(followers__isnull=False).iterator():
            refresh_feed(podcast.id)

        print("Queueing downloads for subscribed feeds ...")
        for podcast in Podcast.objects.filter(subscribers__isnull=False).iterator():
            podcast.queue_missing_episodes_download_tasks(
                storage_directory=psettings.storage_directory,
                naming_scheme=psettings.naming_scheme,
            )

    print("All done for now.")


@background()
def refresh_feed(podcast_id):
    try:
        podcast = Podcast.objects.get(id=podcast_id)
        podcast.update()
    except Exception:
        logger.exception("Refresh task failed", exc_info=True)
