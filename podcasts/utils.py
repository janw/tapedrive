
import feedparser
from feedparser import CharacterEncodingOverride
from dateutil import parser as dateparser
import urllib
from urllib.request import urlopen, Request
from urllib.parse import urlparse
from shutil import copyfileobj, move
import time
import os
import tempfile
import logging
import bleach


# Get an instance of a logger
logger = logging.getLogger(__name__)

USER_AGENT = 'Podcast-Archive/0.1 (https://github.com/janwh/selfhosted-podcast-archive)'

_headers = {'User-Agent': USER_AGENT}
_global_info_keys = ['author', 'language', 'link', 'subtitle', 'title', 'image',
                     'itunes_explicit', 'itunes_type', 'generator', 'updated', 'summary']
_episode_info_keys = ['link', 'subtitle', 'title', 'published', 'description', 'guid']

CLEAN_HTML_GLOBAL = ['summary', 'subtitle', ]
CLEAN_HTML_EPISODE = ['description', 'subtitle', ]


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
            if key in CLEAN_HTML_GLOBAL:
                feed_info_dict[key] = clean_html(feed_info_dict[key])

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
        if key in CLEAN_HTML_GLOBAL:
            episode_info[key] = clean_html(episode_info[key])

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


def chunks(l, n):
    # For item i in a range that is a length of l,
    for i in range(0, len(l), n):
        # Create an index range for l of n items:
        yield l[i:i + n]


def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            print('%r  %2.2f ms' %
                  (method.__name__, (te - ts) * 1000))
        return result
    return timed


def download_file(link, filename):
    logger = logging.getLogger('podcasts.utils.download_file')

    if os.path.isfile(filename):
        logger.error('File at %s already exists' % filename)
        raise FileExistsError('File aready exists')

    # Begin downloading, resolve redirects
    prepared_request = Request(link, headers=_headers)
    try:
        with tempfile.NamedTemporaryFile(delete=False) as outfile:
            with urlopen(prepared_request) as response:
                # Check for proper content length, with resolved link
                link = response.geturl()
                total_size = int(response.getheader('content-length', '0'))
                if total_size == 0:
                    logger.error('Received content-length is 0')
                    raise urllib.error.ContentTooShortError()

                logger.debug('Resolved link:', link)

                # Create the subdir, if it does not exist
                os.makedirs(os.path.dirname(filename), exist_ok=True)

                # Finally start the download for real
                copyfileobj(response, outfile)

        move(outfile.name, filename)
        return total_size

    except (urllib.error.HTTPError,
            urllib.error.URLError) as error:
        logger.error("Download failed. Query returned '%s'" % error)
    except KeyboardInterrupt:
        logger.warning("Unexpected interruption. Deleting unfinished file")
        os.remove(filename)
        raise


def strip_url(link):
    linkpath = urlparse(link).path
    extension = os.path.splitext(linkpath)[1]
    return linkpath, extension


def clean_html(html):

    allowed_tags = bleach.sanitizer.ALLOWED_TAGS
    allowed_tags.append('img')

    allowed_attrs = bleach.sanitizer.ALLOWED_ATTRIBUTES
    allowed_attrs['img'] = ['alt', 'title']

    return bleach.clean(
        html,
        tags=allowed_tags,
        attributes=allowed_attrs)
