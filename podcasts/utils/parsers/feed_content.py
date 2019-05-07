from dateutil import parser as dateparser

from django.template.defaultfilters import slugify

from podcasts.utils.sanitizers import (
    sanitize_summary,
    sanitize_subtitle,
    sanitize_shownotes,
)

# Summary, Subtitle not included, parsed separately
PODCAST_INFO_KEYS = [
    "author",
    "language",
    "link",
    "title",
    "image",
    "itunes_explicit",
    "itunes_type",
    "generator",
    "updated",
]

EPISODE_INFO_KEYS = ["link", "subtitle", "title", "published", "description", "guid"]


def parse_chapters(object):
    chapters = []
    if "psc_chapters" in object:
        chapters = object["psc_chapters"].get("chapters", [])
        for i, chap in enumerate(chapters):
            chapters[i]["starttime"] = chap["start_parsed"]
            del chapters[i]["start_parsed"]
            del chapters[i]["start"]

            if "href" in chap:
                chapters[i]["link"] = chap["href"]
                del chapters[i]["href"]

    return chapters


def parse_feed_info(parsed_feed):
    feed_info = {}

    feed = parsed_feed["feed"]
    for key in PODCAST_INFO_KEYS:
        feed_info[key] = feed.get(key, None)

        if key == "updated" and feed_info[key] is not None:
            feed_info[key] = dateparser.parse(feed_info[key])
        elif key == "image" and "href" in feed_info[key].keys():
            feed_info[key] = feed_info[key]["href"]

    feed_info["subtitle"] = sanitize_subtitle(feed)
    feed_info["summary"] = sanitize_summary(feed)

    # Process episode list separately
    episode_list = parsed_feed.get("items", False) or parsed_feed.get("entries", False)
    if episode_list:
        feed_info["episodes"] = [
            parse_episode_info(episode) for episode in episode_list
        ]
    else:
        feed_info["episodes"] = []

    return feed_info


def parse_episode_info(episode):
    episode_info = {}
    for key in EPISODE_INFO_KEYS:
        episode_info[key] = episode.get(key, None)

        if key == "published" and episode_info[key] is not None:
            episode_info[key] = dateparser.parse(episode_info[key])
        elif (
            key == "image"
            and episode_info.get(key, None) is not None
            and "href" in episode_info[key].keys()
        ):
            episode_info[key] = episode_info[key]["href"]
        elif key == "title":
            episode_info["slug"] = slugify(episode_info["title"])

    episode_info["subtitle"] = sanitize_subtitle(episode)
    episode_info["description"] = sanitize_summary(episode)
    episode_info["shownotes"] = sanitize_shownotes(episode)
    episode_info["chapters"] = parse_chapters(episode)

    episode_info["media_url"] = None
    for link in episode["links"]:
        if "rel" in link.keys() and link["rel"] == "enclosure":
            episode_info["media_url"] = link["href"]

    return episode_info
