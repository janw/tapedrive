
import feedparser
from feedparser import CharacterEncodingOverride
from dateutil import parser as dateparser
from PIL import Image

USER_AGENT = 'Podcast-Archive/0.1 (https://github.com/janwh/selfhosted-podcast-archive)'

_headers = {'User-Agent': USER_AGENT}
_global_info_keys = ['author', 'language', 'link', 'subtitle', 'title', 'image',
                     'itunes_explicit', 'itunes_type', 'generator', 'updated', 'summary']
_episode_info_keys = ['author', 'link', 'subtitle', 'title', ]
_date_keys = ['published', ]


def refresh_feed(feed_url):
    feedparser.USER_AGENT = USER_AGENT
    feedobj = feedparser.parse(feed_url)

    # Escape improper feed-URL
    if 'status' in feedobj.keys() and feedobj['status'] >= 400:
        print("\nQuery returned HTTP error", feedobj['status'])
        return None

    # Escape malformatted XML
    if feedobj['bozo'] == 1:

        # If character encoding is wrong, we continue when reparsing succeeded
        if type(feedobj['bozo_exception']) is not CharacterEncodingOverride:
            print('\nDownloaded feed is malformatted on', feed_url)
            return None

    return parse_feed_info(feedobj)


def parse_feed_info(feedobj):
    feed_info_dict = {}
    if 'feed' in feedobj:
        for key in _global_info_keys:
            feed_info_dict[key] = feedobj['feed'].get(key, None)

            if key == 'updated':
                feed_info_dict[key] = dateparser.parse(feed_info_dict[key])
            elif key == 'image' and 'href' in feed_info_dict[key].keys():
                feed_info_dict[key] = feed_info_dict[key]['href']

    return feed_info_dict

