from django.utils.text import format_lazy
from django.template.defaultfilters import slugify, date as _date
import feedparser
from feedparser import CharacterEncodingOverride
from dateutil import parser as dateparser
import urllib
from urllib.request import urlopen, Request
from urllib.parse import urlparse
from shutil import copyfileobj, move
import os
import tempfile
import logging
import bleach
from markdown import markdown
from string import Template

# Get an instance of a logger
logger = logging.getLogger(__name__)

USER_AGENT = 'Podcast-Archive/0.1 (https://github.com/janwh/selfhosted-podcast-archive)'
HEADERS = {'User-Agent': USER_AGENT}

# Summary, Subtitle not included, parsed separately
PODCAST_INFO_KEYS = ['author', 'language', 'link', 'title', 'image',
                     'itunes_explicit', 'itunes_type', 'generator', 'updated', ]

EPISODE_INFO_KEYS = ['link', 'subtitle', 'title', 'published', 'description', 'guid']

CLEAN_HTML_GLOBAL = ['summary', 'subtitle', ]
CLEAN_HTML_EPISODE = ['description', 'subtitle', ]


ALLOWED_HTML_TAGS = [
    'a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li', 'ol', 'p', 'strong', 'ul']

ALLOWED_HTML_ATTRIBUTES = {
    'a': ['href', 'title'],
    'acronym': ['title'],
    'abbr': [u'title']
}

# Mappings of usable segment => field name
AVAILABLE_PODCAST_SEGMENTS = {
    'podcast_slug': 'slug',
    'podcast_type': 'itunes_type',
    'podcast_title': 'title',
    'podcast_subtitle': 'subtitle',
    'podcast_author': 'author',
    'podcast_language': 'language',
    'podcast_explicit': 'itunes_explicit',
    'podcast_updated': 'updated',
}

AVAILABLE_EPISODE_SEGMENTS = {
    'episode_slug': 'slug',
    'episode_id': 'id',
    'episode_date': 'published',
    'episode_number': 'itunes_episode',
    'episode_type': 'itunes_episodetype',
    'episode_title': 'title',
}

UNIFYING_EPISODE_SEGMENTS = [
    'episode_slug',
    'episode_id',
    'episode_date',
    'episode_number',
    'episode_title',
]

ALL_VALID_SEGMENTS = {**AVAILABLE_EPISODE_SEGMENTS, **AVAILABLE_PODCAST_SEGMENTS}


def get_segments_html(segments):
    if isinstance(segments, dict):
        segments = list(segments.keys())
    return '<code>$' + '</code>, <code>$'.join(segments) + '</code>'


def resolve_segments(string):
    return format_lazy(
        string,
        podcast_segments=get_segments_html(AVAILABLE_PODCAST_SEGMENTS),
        episode_segments=get_segments_html(AVAILABLE_EPISODE_SEGMENTS),
        unifying_segments=get_segments_html(UNIFYING_EPISODE_SEGMENTS),
    )


def construct_download_filename(naming_scheme, episode):
    info = {}
    for key, value in AVAILABLE_EPISODE_SEGMENTS.items():
        info[key] = getattr(episode, value, '')
    for key, value in AVAILABLE_PODCAST_SEGMENTS.items():
        info[key] = getattr(episode.podcast, value, '')

        if key == 'episode_id':
            info[key] = str(info[key])
        # elif key.endswith('_date'):
        #     info[key] = _date(info[key], )

    filename = Template(naming_scheme)
    filename = filename.safe_substitute(info)
    return filename


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


def sanitize_subtitle(object):
    # Properly process subtitle
    if 'subtitle' in object:
        # As per spec, subtitle should be plain text and up to 255 characters.
        subtitle = bleach.clean(object['subtitle'], tags=[], strip=True)
        if len(subtitle) > 255:
            subtitle = subtitle[:251] + ' ...'
        return subtitle


def sanitize_summary(object):
    # Properly process summary/description
    if 'summary_detail' in object:
        # If summary properly announces as markdown parse it out
        if object['summary_detail']['type'] == 'text/markdown':
            html = markdown(object['summary_detail']['value'])
        else:
            html = object['summary_detail']['value']
    elif 'summary' in object:
        html = object.get('summary', '')
    else:
        html = object.get('description', '')

    # In any case, clean the thing from weird HTML shenanigans
    return bleach.clean(
        html,
        tags=ALLOWED_HTML_TAGS,
        attributes=ALLOWED_HTML_ATTRIBUTES,
        strip=True)


def parse_feed_info(parsed_feed):
    feed_info = {}
    if 'feed' not in parsed_feed:
        raise Exception('Feed is incomplete')

    feed = parsed_feed['feed']
    for key in PODCAST_INFO_KEYS:
        feed_info[key] = feed.get(key, None)

        if key == 'updated' and feed_info[key] is not None:
            feed_info[key] = dateparser.parse(feed_info[key])
        elif key == 'image' and 'href' in feed_info[key].keys():
            feed_info[key] = feed_info[key]['href']

    feed_info['subtitle'] = sanitize_subtitle(feed)
    feed_info['summary'] = sanitize_summary(feed)

    # Process episode list separately
    episode_list = parsed_feed.get('items', False) or parsed_feed.get('entries', False)
    if episode_list:
        feed_info['episodes'] = [parse_episode_info(episode) for episode in episode_list]
    else:
        feed_info['episodes'] = []

    return feed_info


def parse_episode_info(episode):
    episode_info = {}
    for key in EPISODE_INFO_KEYS:
        episode_info[key] = episode.get(key, None)

        if key == 'published' and episode_info[key] is not None:
            episode_info[key] = dateparser.parse(episode_info[key])
        elif (key == 'image' and
              episode_info.get(key, None) is not None and
              'href' in episode_info[key].keys()):
            episode_info[key] = episode_info[key]['href']
        elif key == 'title':
            episode_info['slug'] = slugify(episode_info['title'])

    episode_info['subtitle'] = sanitize_subtitle(episode)
    episode_info['description'] = sanitize_summary(episode)

    episode_info['media_url'] = None
    for link in episode['links']:
        if 'rel' in link.keys() and link['rel'] == 'enclosure':
            episode_info['media_url'] = link['href']

    return episode_info


def chunks(l, n):
    # For item i in a range that is a length of l,
    for i in range(0, len(l), n):
        # Create an index range for l of n items:
        yield l[i:i + n]


def download_file(link, filename):
    logger = logging.getLogger('podcasts.utils.download_file')

    if os.path.isfile(filename):
        logger.error('File at %s already exists' % filename)
        raise FileExistsError('File aready exists')

    # Begin downloading, resolve redirects
    prepared_request = Request(link, headers=HEADERS)
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
