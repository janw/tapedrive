from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone

from podcasts.models import PodcastsSettings
from podcasts.models.episode import Episode
from podcasts.models.podcast import Podcast
from podcasts.utils import download_file

from background_task import background

User = get_user_model()


@background()
def download_episode(media_url, file_path, id):

    # Get Episode from database
    episode = Episode.objects.get(id=id)
    print('Downloading episode %s ...' % episode)

    # Download the file
    filesize = download_file(media_url, file_path)

    # Update Episode after download
    episode.file_size = filesize
    episode.downloaded = timezone.now()
    episode.save()


@background(queue='low-priority')
def regular_feed_refresh():
    psettings = PodcastsSettings.objects.get(site__id=getattr(settings, 'SITE_ID', 1))

    print('Refreshing followed feeds ...')
    # Refresh feeds of podcasts with at least one follower
    for podcast in Podcast.objects.filter(followers__isnull=False).iterator():
        podcast.update()
        podcast.save()

    print('Queueing downloads for subscribed feeds ...')
    for podcast in Podcast.objects.filter(subscribers__isnull=False).iterator():
        podcast.queue_missing_episodes_download_tasks(
            storage_directory=psettings.storage_directory,
            naming_scheme=psettings.naming_scheme)

    print('All done for now.')
