from django.contrib.auth import get_user_model
from django.utils import timezone

from podcasts.models.episode import Episode
from podcasts.utils import construct_download_filename, download_file, strip_url
from podcasts.conf import *

from background_task import background
import os

User = get_user_model()


@background()
def download_episode(media_url, file_path, id):

    # Download the file
    filesize = download_file(media_url, file_path)

    # Update Episode after download
    episode = Episode.objects.get(id=id)
    episode.file_size = filesize
    episode.downloaded = timezone.now()
    episode.save()
