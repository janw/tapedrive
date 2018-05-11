from django.contrib.auth import get_user_model
from django.utils import timezone
from podcasts.models.episode import Episode
from .utils import download_file, strip_url
from .conf import *

from background_task import background
import os

User = get_user_model()


@background()
def download_episode(**kwargs):

    episode = Episode.objects.get(**kwargs)
    linkpath, extension = strip_url(episode.media_url)

    # Get filename
    filename = "{podcast_slug}/{episode_title}".format(
        podcast_slug=episode.podcast.slug,
        episode_title=episode.title,
    ) + extension
    target = os.path.join(STORAGE_DIRECTORY, filename)
    filesize = download_file(episode.media_url, target)

    episode.file_path = target
    episode.file_size = filesize
    episode.downloaded = timezone.now()
    episode.save()
