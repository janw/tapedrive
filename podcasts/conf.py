from datetime import timedelta

from django.conf import settings

from .apps import PodcastsConfig


def _getattr(variable, default):
    prefix = PodcastsConfig.name.upper()
    variable = variable.upper()
    return getattr(settings, f"{prefix}_{variable}", default)


STORAGE_DIRECTORY = "/data"
DEFAULT_NAMING_SCHEME = "$podcast_slug/$episode_slug"
DEFAULT_DATE_FORMAT = "Y-m-d_Hi"

ITUNES_TOPCHARTS_URL = "https://rss.itunes.apple.com/api/v1/us/podcasts/top-podcasts/all/25/explicit.json"
ITUNES_SEARCH_URL = "https://itunes.apple.com/search?"
ITUNES_LOOKUP_URL = "https://itunes.apple.com/lookup?"
ITUNES_SEARCH_LIMIT = 15

# DEFAULT_REFRESH_RATE = Task.HOURLY
DEFAULT_REFRESH_PRIORITY = -10
DEFAULT_REFRESH_DELAY = timedelta(minutes=1)


DEFAULT_PODCASTS_PER_PAGE = 15
DEFAULT_EPISODES_PER_PAGE = 30
DEFAULT_DEFAULT_PODCASTS_ORDER = "title"
DEFAULT_DEFAULT_EPISODES_ORDER = "-published"
DEFAULT_DEFAULT_IMAGE_SECURITY_POLICY = "f"
DEFAULT_SEEK_FORWARD_BY = 45
DEFAULT_SEEK_BACKWARD_BY = 30
