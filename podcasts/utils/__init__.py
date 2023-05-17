import logging
import os
import tempfile
import xml.etree.ElementTree as etree
from collections import namedtuple
from functools import lru_cache
from io import BytesIO
from shutil import copyfileobj, move
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse, urlunparse
from urllib.request import Request, urlopen

import feedparser
import requests
from django.core.files import File
from feedparser import CharacterEncodingOverride

from podcasts.utils.filters import shownotes_image_cleaner
from podcasts.utils.parsers.feed_content import parse_feed_info

# Get an instance of a logger
logger = logging.getLogger(__name__)

USER_AGENT = "Podcast-Archive/0.1 (https://github.com/janw/tapedrive)"
HEADERS = {"User-Agent": USER_AGENT}

session = requests.Session()
session.headers.update(HEADERS)

feed_info = namedtuple("feed_info", ["data", "url", "next_page", "last_page"])


def refresh_feed(feed_url):
    response = session.get(feed_url, allow_redirects=True)
    response.raise_for_status()

    feedobj = feedparser.parse(response.content)

    # Escape malformatted XML
    if feedobj["bozo"] == 1 and type(feedobj["bozo_exception"]) is not CharacterEncodingOverride:
        raise Exception("Feed is malformatted")

    if "feed" not in feedobj:
        raise Exception("Feed is incomplete")

    links = feedobj["feed"].get("links", [])
    next_page = next((item for item in links if item["rel"] == "next"), {}).get("href")
    last_page = next((item for item in links if item["rel"] == "last"), {}).get("href")

    if next_page:
        logger.info("Feed has next page")

    return feed_info(parse_feed_info(feedobj), response.url, next_page, last_page)


def replace_shownotes_images(content, allowed_domains=False):
    if len(allowed_domains) == 1 and allowed_domains[0] == "*":
        return content
    else:
        return shownotes_image_cleaner.clean(content, allowed_domains=allowed_domains)


def chunks(l, n):  # noqa: E741
    # For item i in a range that is a length of l,
    for i in range(0, len(l), n):
        # Create an index range for l of n items:
        yield l[i : i + n]


def download_file(link, filename):
    logger = logging.getLogger("podcasts.utils.download_file")

    if os.path.isfile(filename):
        logger.error("File at %s already exists" % filename)
        return

    # Begin downloading, resolve redirects
    prepared_request = Request(link, headers=HEADERS)
    try:
        with tempfile.NamedTemporaryFile(delete=False) as outfile, urlopen(prepared_request) as response:
            # Check for proper content length, with resolved link
            link = response.geturl()
            total_size = int(response.getheader("content-length", "0"))
            if total_size == 0:
                logger.error("Received content-length is 0")
                return

            logger.debug("Resolved link:", link)

            # Create the subdir, if it does not exist
            os.makedirs(os.path.dirname(filename), exist_ok=True)

            # Finally start the download for real
            copyfileobj(response, outfile)

        move(outfile.name, filename)
        return total_size

    except (HTTPError, URLError) as error:
        logger.error("Download failed. Query returned '%s'" % error)
        return
    except KeyboardInterrupt:
        logger.error("Unexpected interruption. Deleting unfinished file")
        os.remove(filename)
        return


@lru_cache(maxsize=256)
def download_cover(img_url):
    logger.info(f"Downloading cover {img_url}")

    # Remove query params from URL (could be size-restricting, example: NPR's Invisibilia)
    # Of course that does not work on for example private feeds that use query params for
    # authentication (example: Do By Friday Aftershow delivered via Patreon using
    # token-time&token-hash)
    url = urlparse(img_url)
    logger.debug("Query params (removed on first try): %s", url.query)
    url = url._replace(query="")
    unqueried_img_url = urlunparse(url)
    response = session.get(unqueried_img_url, allow_redirects=True)
    if response.status_code >= 400:
        logger.info("Failed without query string, trying again.")
        # If that fails, try again with the original URL. After that fail softly
        response = session.get(img_url, allow_redirects=True)
        if response.status_code >= 400:
            return
        logger.info("Success.")

    name = url.path.split("/")[-1]
    finput = BytesIO(response.content)
    return File(finput, name=name)


def strip_url(link):
    linkpath = urlparse(link).path
    extension = os.path.splitext(linkpath)[1]
    return linkpath, extension


def handle_uploaded_file(f):
    with tempfile.NamedTemporaryFile(delete=False) as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return destination.name


def parse_opml_file(filename):
    with open(filename) as file:
        tree = etree.fromstringlist(file)
    return [node.get("xmlUrl") for node in tree.findall("*/outline/[@type='rss']") if node.get("xmlUrl") is not None]


def unify_apple_podcasts_response(data):
    if "feed" in data:
        data["results"] = data["feed"]["results"]
        data["resultsCount"] = len(data["results"])
    for i, result in enumerate(data["results"]):
        if "collectionId" in result:
            data["results"][i]["id"] = int(result["collectionId"])
        else:
            data["results"][i]["id"] = int(result["id"])
        if "collectionName" in result:
            data["results"][i]["name"] = result["collectionName"]

        if "artworkUrl600" in result:
            data["results"][i]["artworkUrl"] = result["artworkUrl600"]
        elif "artworkUrl100" in result:
            data["results"][i]["artworkUrl"] = result["artworkUrl100"]

        if "genres" in result and isinstance(result["genres"][0], dict):
            data["results"][i]["genres"] = [{"name": item.get("name")} for item in result["genres"]]

    return data
