from django.utils.text import format_lazy
from django.utils.translation import gettext as _
from django.template.defaultfilters import slugify
from django.conf import settings


from collections import namedtuple
from dateutil import parser as dateparser
from feedparser import CharacterEncodingOverride
from io import BytesIO
from markdown import markdown
from PIL import Image
from shutil import copyfileobj, move
from urllib.parse import urlparse, urlunparse
from urllib.request import urlopen, Request
from bleach.sanitizer import Cleaner
from html5lib.filters.base import Filter
import feedparser
import logging
import os
import requests
import tempfile
import urllib
import xml.etree.ElementTree as etree
from bs4 import BeautifulSoup


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

EXTENDED_HTML_TAGS = [
    'h1', 'h2', 'h3' 'h4', 'h5', 'h6', 'img', 'table', 'thead', 'tbody', 'tr', 'th', 'td']

EXTENDED_HTML_ATTRIBUTES = {
    'img': ['rel', 'src', 'alt'],
    'td': ['colspan', 'rowspan'],

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

feed_info = namedtuple("feed_info", ['data', 'url', 'next_page', 'last_page'])


class CleanerWithOptions(Cleaner):
    def clean(self, text, allowed_domains=[]):
        import six
        from bleach.utils import force_unicode
        from bleach.sanitizer import BleachSanitizerFilter

        if not isinstance(text, six.string_types):
            message = "argument cannot be of '{name}' type, must be of text type".format(
                name=text.__class__.__name__)
            raise TypeError(message)

        if not text:
            return u''

        text = force_unicode(text)
        dom = self.parser.parseFragment(text)
        filtered = BleachSanitizerFilter(
            source=self.walker(dom),

            # Bleach-sanitizer-specific things
            attributes=self.attributes,
            strip_disallowed_elements=self.strip,
            strip_html_comments=self.strip_comments,

            # html5lib-sanitizer things
            allowed_elements=self.tags,
            allowed_css_properties=self.styles,
            allowed_protocols=self.protocols,
            allowed_svg_properties=[],
        )

        # Apply any filters after the BleachSanitizerFilter
        for filter_class in self.filters:
            fc = filter_class(source=filtered)
            filtered = fc.__iter__(allowed_domains=allowed_domains)

        return self.serializer.render(filtered)


class ImgSrcFilter(Filter):
    def __iter__(self, **kwargs):
        allowed_domains = kwargs.pop('allowed_domains', [])
        for token in Filter.__iter__(self):
            if token['type'] in ['StartTag', 'EmptyTag'] and token['data']:
                data_alt = None
                data_src = None
                for attr, value in token['data'].items():
                    if attr[1] == 'alt':
                        data_alt = token['data'][attr]
                    elif attr[1] == 'src':
                        data_src = token['data'][attr]

                if data_src:
                    domain = clean_link(data_src)
                    if domain not in allowed_domains:
                        token['data'][(None, 'data-src')] = data_src
                        token['data'][(None, 'class')] = 'has-src'
                        token['data'][(None, 'alt')] = format_lazy('Image from {domain}',
                                                                   domain=domain)
                        token['data'][(None, 'src')] = ''
                        if data_alt:
                            token['data'][(None, 'data-alt')] = data_alt
            yield token


subtitle_cleaner = Cleaner(tags=[], strip=True)

summary_cleaner = Cleaner(tags=ALLOWED_HTML_TAGS, attributes=ALLOWED_HTML_ATTRIBUTES, strip=True)

shownotes_cleaner = Cleaner(tags=ALLOWED_HTML_TAGS + EXTENDED_HTML_TAGS,
                            attributes={**ALLOWED_HTML_ATTRIBUTES, **EXTENDED_HTML_ATTRIBUTES},
                            strip=True)


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


def refresh_feed(feed_url):
    try:
        response = requests.get(feed_url, headers=HEADERS, allow_redirects=True)
    except requests.exceptions.ConnectionError:
        logger.error('Connection error')
        return None

    # Escape improper feed-URL
    if response.status_code >= 400:
        logger.error('HTTP error %d: %s' % (response.status_code, response.reason))
        return None

    feedobj = feedparser.parse(response.content)

    # Escape malformatted XML
    if feedobj['bozo'] == 1 and type(feedobj['bozo_exception']) is not CharacterEncodingOverride:
        logger.error('Feed is malformatted')
        return None

    if 'feed' not in feedobj:
        logger.error('Feed is incomplete')
        return None

    links = feedobj['feed'].get('links', [])
    next_page = next((item for item in links if item["rel"] == "next"), {}).get('href')
    last_page = next((item for item in links if item["rel"] == "last"), {}).get('href')

    if next_page:
        logger.info('Feed has next page')

    return feed_info(parse_feed_info(feedobj), response.url, next_page, last_page)


def sanitize_subtitle(object):
    # Properly process subtitle
    if 'subtitle' in object:
        # As per spec, subtitle should be plain text and up to 255 characters.
        subtitle = subtitle_cleaner.clean(object.get('subtitle', ''))
        if len(subtitle) > 255:
            logger.warning('Subtitle too long, will be truncated')
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
    return summary_cleaner.clean(html)


def sanitize_shownotes(object, max_headline=2):
    content = object.get('content')
    if not content:
        return None

    html = max(content, key=lambda c: len(c.get('value', ''))).get('value', '')
    soup = BeautifulSoup(html, 'html.parser')
    for script in soup.find_all('script'):
        script.decompose()
    adjust_headline_levels(soup, max_headline)
    return shownotes_cleaner.clean(str(soup))


def replace_shownotes_images(content, allowed_domains=[]):
    if len(allowed_domains) == 1 and allowed_domains[0] == '*':
        return content
    else:
        cleaner = CleanerWithOptions(tags=ALLOWED_HTML_TAGS + EXTENDED_HTML_TAGS,
                                     attributes={**ALLOWED_HTML_ATTRIBUTES, **EXTENDED_HTML_ATTRIBUTES},
                                     strip=True, filters=[ImgSrcFilter])
        return cleaner.clean(content, allowed_domains=allowed_domains)


def adjust_headline_levels(soup, max_level=3):
    top_level_content = 1
    for level in range(1, 6):
        if soup.find('h%d' % level):
            top_level_content = level
            break

    if top_level_content < max_level:
        transposal = max_level - top_level_content
        logger.info('Transposing headline levels by %d' % transposal)

        for level in reversed(range(1, 5)):
            newlevel = min((level + transposal, 6))
            for h in soup.find_all('h%d' % level):
                new_tag = soup.new_tag('h%d' % newlevel)
                new_tag.string = h.string
                h.replace_with(new_tag)


def parse_feed_info(parsed_feed):
    feed_info = {}

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
    episode_info['shownotes'] = sanitize_shownotes(episode)

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
        return

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
                    return

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
        return
    except KeyboardInterrupt:
        logger.error("Unexpected interruption. Deleting unfinished file")
        os.remove(filename)
        return


def download_cover(img_url, file):
    logger.info('Downloading cover')

    # Remove query params from URL (could be size-restricting, example: NPR's Invisibilia)
    # Of course that does not work on for example private feeds that use query params for
    # authentication (example: Do By Friday Aftershow delivered via Patreon using
    # token-time&token-hash)
    url = urlparse(img_url)
    logger.debug('Query params (removed on first try): %s', url.query)
    url = url._replace(query='')
    unqueried_img_url = urlunparse(url)
    response = requests.get(unqueried_img_url, headers=HEADERS, allow_redirects=True)
    if response.status_code >= 400:
        logger.info('Failed without query string, trying again.')
        # If that fails, try again with the original URL. After that fail softly
        response = requests.get(img_url, headers=HEADERS, allow_redirects=True)
        if response.status_code >= 400:
            return
        else:
            logger.info('Success.')

    name = url.path.split('/')[-1]
    name, ext = os.path.splitext(name)
    target_img_size = getattr(settings, 'COVER_IMAGE_SIZE', (1000, 1000))
    finput = BytesIO(response.content)
    img = Image.open(finput)
    logger.debug('Original image size is %dx%d.' % img.size)

    # Return early and untouched if the image is smaller than desired
    if img.size[0] < target_img_size[0] or img.size[1] < target_img_size[1]:
        logger.info('Image size is smaller than desired. Ain\'t (re)touching that.')
        finput.seek(0)
        file.write(finput.read())
        file.seek(0)
        return name + ext

    # Resize the image (from https://djangosnippets.org/snippets/10597/)
    img.thumbnail(target_img_size)

    if ext.lower() != 'png':

        # If the downloaded image has an alpha-channel: fill background
        if img.mode in ('RGBA', 'LA'):
            logger.debug('Non-PNG image with alpha-channel will be placed on white background')
            fill_color = (255, 255, 255, 255)
            background = Image.new(img.mode[:-1], img.size, fill_color)
            background.paste(img, img.split()[-1])
            img = background

        if img.mode != 'RGB':
            img = img.convert('RGB')

        # After modifications, save it to the output
        img.save(file, format='JPEG', quality=95)
        name += 'jpg'
    else:
        img.save(file, format='PNG', transparency=False)
        name += 'png'

    file.seek(0)
    return name


def strip_url(link):
    linkpath = urlparse(link).path
    extension = os.path.splitext(linkpath)[1]
    return linkpath, extension


def clean_link(link, include_path=False):
    parsed = urlparse(link)
    netloc = parsed.netloc
    if parsed.netloc.startswith('www.'):
        netloc = netloc[4:]

    if include_path:
        path = parsed.path.rstrip('/')
        splits = str.split(path, '/')
        if len(splits) > 2:
            path = '/…/' + splits[-1]

        return netloc + path
    return netloc


def handle_uploaded_file(f):
    with tempfile.NamedTemporaryFile(delete=False) as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return destination.name


def parse_opml_file(filename):
    with open(filename) as file:
        tree = etree.fromstringlist(file)
    return [node.get('xmlUrl') for node
            in tree.findall("*/outline/[@type='rss']")
            if node.get('xmlUrl') is not None]


def unify_apple_podcasts_response(data):
    if 'feed' in data:
        data['results'] = data['feed']['results']
        data['resultsCount'] = len(data['results'])
    for i, result in enumerate(data['results']):
        if 'collectionId' in result:
            data['results'][i]['id'] = int(result['collectionId'])
        else:
            data['results'][i]['id'] = int(result['id'])
        if 'collectionName' in result:
            data['results'][i]['name'] = result['collectionName']

        if 'artworkUrl600' in result:
            data['results'][i]['artworkUrl'] = result['artworkUrl600']
        elif 'artworkUrl100' in result:
            data['results'][i]['artworkUrl'] = result['artworkUrl100']

        if 'genres' in result and isinstance(result['genres'][0], dict):
            data['results'][i]['genres'] = [dict(name=item.get('name')) for item in result['genres']]

    return data
