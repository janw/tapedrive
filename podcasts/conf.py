from django.conf import settings
from .apps import PodcastsConfig
import os
from tempfile import TemporaryDirectory
from html5lib.constants import namespaces as html_namespaces


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

STORAGE_DIRECTORY = '$HOME/'
DEFAULT_NAMING_SCHEME = '{podcast_slug}/{episode_title}'
