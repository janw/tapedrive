import logging

from bs4 import BeautifulSoup
from markdown import markdown

from podcasts.utils.filters import subtitle_cleaner, summary_cleaner, shownotes_cleaner


logger = logging.getLogger(__name__)


def sanitize_subtitle(object):
    # Properly process subtitle
    if "subtitle" in object:
        # As per spec, subtitle should be plain text and up to 255 characters.
        subtitle = subtitle_cleaner.clean(object.get("subtitle", ""))
        if len(subtitle) > 255:
            logger.warning("Subtitle too long, will be truncated")
            subtitle = subtitle[:251] + " ..."
        return subtitle


def sanitize_summary(object):
    # Properly process summary/description
    if "summary_detail" in object:
        # If summary properly announces as markdown parse it out
        if object["summary_detail"]["type"] == "text/markdown":
            html = markdown(object["summary_detail"]["value"])
        else:
            html = object["summary_detail"]["value"]
    elif "summary" in object:
        html = object.get("summary", "")
    else:
        html = object.get("description", "")

    # In any case, clean the thing from weird HTML shenanigans
    return summary_cleaner.clean(html)


def sanitize_shownotes(object, max_headline=2):
    content = object.get("content")
    if not content:
        return None

    html = max(content, key=lambda c: len(c.get("value", ""))).get("value", "")
    soup = BeautifulSoup(html, "html.parser")
    for script in soup.find_all("script"):
        script.decompose()
    adjust_headline_levels(soup, max_headline)
    return shownotes_cleaner.clean(str(soup))


def adjust_headline_levels(soup, max_level=3):
    top_level_content = 1
    for level in range(1, 6):
        if soup.find("h%d" % level):
            top_level_content = level
            break

    if top_level_content < max_level:
        transposal = max_level - top_level_content
        for level in reversed(range(1, 5)):
            newlevel = min((level + transposal, 6))
            for h in soup.find_all("h%d" % level):
                new_tag = soup.new_tag("h%d" % newlevel)
                new_tag.string = h.string
                h.replace_with(new_tag)
