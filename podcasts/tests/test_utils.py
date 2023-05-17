import logging

import pytest
import requests

from podcasts import utils
from podcasts.utils import properties

FIXTURES_URL = "https://raw.githubusercontent.com/janw/tapedrive/main/podcasts/tests/fixtures/"

TEST_FEED = FIXTURES_URL + "valid.xml"
TEST_FEED_MALFORMED = (
    FIXTURES_URL + "literally_nonexistent.xml",  # Not Found
    FIXTURES_URL + "invalid.xml",  # Invalid Feed
)
TEST_FEED_NEXT_PAGE = FIXTURES_URL + "paged_p1.xml"
TEST_FEED_SUBTITLE_TOO_LONG = FIXTURES_URL + "subtitle_too_long.xml"


def test_valid_help_string():
    string = "{podcast_segments}||{episode_segments}||{unifying_segments}"
    should_become = (
        "<code>$podcast_slug</code>, <code>$podcast_type</code>, <code>$podcast_title</code>, <code>$p"
        "odcast_subtitle</code>, <code>$podcast_author</code>, <code>$podcast_language</code>, <code>$"
        "podcast_explicit</code>, <code>$podcast_updated</code>||<code>$episode_slug</code>, <code>$ep"
        "isode_id</code>, <code>$episode_date</code>, <code>$episode_number</code>, <code>$episode_typ"
        "e</code>, <code>$episode_title</code>||<code>$episode_slug</code>, <code>$episode_id</code>, "
        "<code>$episode_date</code>, <code>$episode_number</code>, <code>$episode_title</code>"
    )
    assert properties.resolve_segments(string) == should_become


@pytest.mark.vcr()
def test_valid_feed():
    feed_info = utils.refresh_feed(TEST_FEED)
    assert feed_info is not None
    assert feed_info.data["title"] == "Killing Time"


@pytest.mark.vcr()
@pytest.mark.parametrize("feed,expected,message", [(0, None, "Not Found"), (1, None, "Feed is malformatted")])
def test_invalid_feed(feed, expected, message, caplog):
    """Querying an invalid feed should always fail softly, returning None."""
    caplog.set_level(logging.ERROR, logger="podcasts.utils")
    with pytest.raises(Exception):  # noqa: B017
        utils.refresh_feed(TEST_FEED_MALFORMED[feed])


def test_connection_error(mocker, caplog):
    mock_requests = mocker.patch("podcasts.utils.session.get", side_effect=requests.exceptions.ConnectionError)
    caplog.set_level(logging.ERROR, logger="podcasts.utils")
    with pytest.raises(requests.exceptions.ConnectionError):
        utils.refresh_feed("https://any.feed/is/fine/here")
    mock_requests.assert_called_once()


@pytest.mark.vcr()
def test_paged_feed(caplog):
    """Test proper handling of a paged feed."""
    caplog.set_level(logging.INFO, logger="podcasts.utils")

    feed_info = utils.refresh_feed(TEST_FEED_NEXT_PAGE)
    assert feed_info.next_page is not None
    assert "Feed has next page" in caplog.text


@pytest.mark.vcr()
def test_long_subtitle_feed(caplog):
    """Test if an overly long subtitle is properly truncated"""
    caplog.set_level(logging.WARNING, logger="podcasts.utils")
    feed_info = utils.refresh_feed(TEST_FEED_SUBTITLE_TOO_LONG)
    assert len(feed_info.data["subtitle"]) == 255
    assert feed_info.data["subtitle"].endswith(" ...")
    assert "Subtitle too long, will be truncated" in caplog.text
