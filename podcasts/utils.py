
import feedparser
from feedparser import CharacterEncodingOverride
from dateutil import parser as dateparser
from PIL import Image
import hashlib

USER_AGENT = 'Podcast-Archive/0.1 (https://github.com/janwh/selfhosted-podcast-archive)'

_headers = {'User-Agent': USER_AGENT}
_global_info_keys = ['author', 'language', 'link', 'subtitle', 'title', 'image',
                     'itunes_explicit', 'itunes_type', 'generator', 'updated', 'summary']
_episode_info_keys = ['link', 'subtitle', 'title', 'published', 'description', 'guid']


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

            if key == 'updated' and feed_info_dict[key] is not None:
                feed_info_dict[key] = dateparser.parse(feed_info_dict[key])
            elif key == 'image' and 'href' in feed_info_dict[key].keys():
                feed_info_dict[key] = feed_info_dict[key]['href']

        episode_list = feedobj.get('items', False) or feedobj.get('entries', False)
        if episode_list:
            feed_info_dict['episodes'] = [parse_episode_info(episode) for episode in episode_list]
        else:
            feed_info_dict['episodes'] = []

    return feed_info_dict


def parse_episode_info(episode):
    episode_info = {}
    for key in _episode_info_keys:
        episode_info[key] = episode.get(key, None)

        if key == 'published' and episode_info[key] is not None:
            episode_info[key] = dateparser.parse(episode_info[key])
        elif (key == 'image' and
              episode_info.get(key, None) is not None and
              'href' in episode_info[key].keys()):
            episode_info[key] = episode_info[key]['href']

    # media_url = None
    episode_info['media_url'] = None
    for link in episode['links']:
        if 'rel' in link.keys() and link['rel'] == 'enclosure':
            # if link['type'].startswith('audio'):
                # media_url = link['href']
            # elif link['type'].startswith('video'):
                # media_url = link['href']
            episode_info['media_url'] = link['href']

    return episode_info
