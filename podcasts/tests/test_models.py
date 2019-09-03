import logging
from datetime import datetime
from datetime import timezone

import pytest
from django.contrib.sites.models import Site
from django.db import transaction
from django.db.utils import IntegrityError

from podcasts.models import PodcastsSettings
from podcasts.models.episode import Episode
from podcasts.models.podcast import Podcast
from podcasts.tests.test_utils import TEST_FEED_NEXT_PAGE

# Create your tests here.

TEST_FEED = "http://feeds.5by5.tv/killingtime"
TEST_FEED_PAGED = TEST_FEED_NEXT_PAGE

TEST_PODCAST = {
    "feed_url": "http://example.com/feed",
    "title": "Test Feed",
    "itunes_type": "serial",
}
TEST_EPISODE = {
    "title": "Le fancey episode",
    "guid": "http://example.com/feed/01-testep",
    "media_url": "http://example.com/feed/01-testep.mp3",
    "published": datetime(2018, 3, 12, 10, tzinfo=timezone.utc),
}


@pytest.mark.django_db
@pytest.mark.vcr()
def test_podcast_model(caplog):
    """Test creation of Podcast model from different inputs"""
    Podcast.objects.create(feed_url=TEST_FEED)

    podcast = Podcast.objects.get(feed_url=TEST_FEED)
    assert podcast.title == ""

    with pytest.raises(IntegrityError):
        Podcast.objects.create_from_feed_url(TEST_FEED)

    with caplog.at_level(logging.INFO, logger="podcasts.models"):
        podcast.update()

    assert "Fetched Killing Time" in caplog.text
    assert podcast.title == "Killing Time"
    assert podcast.get_absolute_url() == "/podcasts/killing-time/"

    # get_or_create should return the same podcast now
    same_one, created = Podcast.objects.get_or_create_from_feed_url(TEST_FEED)
    assert podcast == same_one
    assert created is False

    # Should have more than 0 episodes
    assert Episode.objects.count() > 0

    # Deletion should remove Podcast and cascade to Episodes
    podcast.delete()
    Podcast.objects.count() == 0
    Episode.objects.count() == 0


@pytest.mark.django_db
@pytest.mark.vcr()
def test_podcast_with_paged_feed(caplog):
    """Create complete Podcast from feed_url, with pages."""

    with caplog.at_level(logging.INFO, logger="podcasts.models"):
        podcast, created = Podcast.objects.get_or_create_from_feed_url(
            TEST_FEED_NEXT_PAGE
        )
    assert created
    assert isinstance(podcast, Podcast)

    assert "Creating CRE" in caplog.text
    assert "No next page found" in caplog.text
    caplog.clear()

    # Update Podcast, detection of existing episodes
    with caplog.at_level(logging.INFO, logger="podcasts.models"):
        podcast.update(insert_cover=False)

    assert "Inserting episodes from first page" in caplog.text
    assert "Found existing episodes" in caplog.text


@pytest.mark.django_db
def test_filename_generation():
    valid_naming_scheme = "$podcast_type/$podcast_slug/${episode_date}_$episode_title"
    invalid_naming_scheme = "$podcast_type/${podcast_slug}_$episode_testattr"
    datefmt = "Y-m-d_Hi"

    podcast = Podcast.objects.create(**TEST_PODCAST)
    episode = podcast.episodes.create(**TEST_EPISODE)

    should_be = "serial/test-feed/2018-03-12_1000_Le fancey episode.mp3"
    file_path = episode.construct_file_path("", valid_naming_scheme, datefmt)
    assert file_path == should_be

    # Check that an invalid segments is untouched
    should_be = "serial/test-feed_$episode_testattr.mp3"
    file_path = episode.construct_file_path("", invalid_naming_scheme, datefmt)
    assert file_path == should_be


@pytest.mark.django_db
def test_settings_model():
    site = Site.objects.create(name="Test Site", domain="testsite.local")

    # Creating a Site object, fires a post_save creation of PodcastsSettings
    # therefore trying to create another PS object with the same Site should
    # cause the unique constraint to kick in
    with pytest.raises(IntegrityError):
        PodcastsSettings.objects.create(site=site)

    # OneToOne rel should contain the PS instance
    settings = site.podcastssettings
    assert isinstance(settings, PodcastsSettings)

    # Return the proper __str__ based on the Site.name
    assert str(settings) == "Test Site Podcasts Settings"


@pytest.mark.django_db
@pytest.mark.vcr()
def test_episode_model():
    podcast = Podcast.objects.create(feed_url=TEST_FEED)
    podcast.update()

    # Episode object cannot be created empty (requires GUID and Podcast)
    with transaction.atomic():
        with pytest.raises(IntegrityError):
            episode = Episode.objects.create()
    with transaction.atomic():
        with pytest.raises(IntegrityError):
            episode = Episode.objects.create(guid="testguid")

    with transaction.atomic():
        episode = Episode.objects.create(guid="/testguid1/", podcast=podcast)
    assert str(episode) == "Killing Time's Episode"

    with transaction.atomic():
        episode = Episode.objects.create(
            guid="/testguid2/", podcast=podcast, title="Fancy Test Episode"
        )
    str(episode) == "Fancy Test Episode"
