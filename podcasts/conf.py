from django.conf import settings
from .apps import PodcastsConfig
import os
from tempfile import TemporaryDirectory


def _getattr(variable, default):
    prefix = PodcastsConfig.name.upper()
    variable = variable.upper()
    return getattr(settings, '%s_%s' % (prefix, variable), default)


# How to display things in frontend
PODCASTS_PER_PAGE = _getattr('PODCASTS_PER_PAGE', 15)
EPISODES_PER_PAGE = _getattr('EPISODES_PER_PAGE', 30)

# Playback-related options (maybe in the future)
SEEK_FORWARD_BY = _getattr('SEEK_FORWARD_BY', 45)
SEEK_BACKWARD_BY = _getattr('SEEK_BACKWARD_BY', 30)

# Storage-related options
if os.path.exists('/Volumes/Storage/'):
    storage_dir = '/Volumes/Storage'
elif os.path.exists('/mnt/storage/'):
    storage_dir = '/mnt/storage'
else:
    storage_dir = TemporaryDirectory()
STORAGE_DIRECTORY = _getattr('STORAGE_DIRECTORY', storage_dir)
