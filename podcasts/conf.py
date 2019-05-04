from django.conf import settings
from .apps import PodcastsConfig
from background_task.models import Task
from datetime import timedelta


def _getattr(variable, default):
    prefix = PodcastsConfig.name.upper()
    variable = variable.upper()
    return getattr(settings, "%s_%s" % (prefix, variable), default)


# How to display things in frontend
PODCASTS_PER_PAGE = _getattr("PODCASTS_PER_PAGE", 15)
EPISODES_PER_PAGE = _getattr("EPISODES_PER_PAGE", 30)

DEFAULT_PODCASTS_ORDER = _getattr("PODCASTS_ORDER", "title")
DEFAULT_EPISODES_ORDER = _getattr("EPISODES_ORDER", "-published")

DEFAULT_IMAGE_SECURITY_POLICY = _getattr("IMAGE_SECURITY_POLICY", "f")

# Playback-related options (maybe in the future)
SEEK_FORWARD_BY = _getattr("SEEK_FORWARD_BY", 45)
SEEK_BACKWARD_BY = _getattr("SEEK_BACKWARD_BY", 30)

STORAGE_DIRECTORY = "/data"
DEFAULT_NAMING_SCHEME = "$podcast_slug/$episode_slug"
DEFAULT_DATE_FORMAT = "Y-m-d_Hi"

ITUNES_TOPCHARTS_URL = (
    "https://rss.itunes.apple.com/api/v1/us/podcasts/top-podcasts/all/25/explicit.json"
)
ITUNES_SEARCH_URL = "https://itunes.apple.com/search?"
ITUNES_LOOKUP_URL = "https://itunes.apple.com/lookup?"
ITUNES_SEARCH_LIMIT = 15

DEFAULT_REFRESH_RATE = Task.HOURLY
DEFAULT_REFRESH_PRIORITY = -10
DEFAULT_REFRESH_DELAY = timedelta(minutes=1)
