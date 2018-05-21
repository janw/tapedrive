from django.test import TestCase

from django.contrib.sites.models import Site
from django.db import transaction
from django.db.utils import IntegrityError
from podcasts.models.episode import Episode
from podcasts.models.podcast import Podcast
from podcasts.models import PodcastsSettings

from datetime import datetime, timezone

# Create your tests here.

TEST_FEED = 'http://feeds.5by5.tv/killingtime'
TEST_FEED_PAGED = 'http://cre.fm/feed/m4a'
TEST_FEED_PAGED_SECOND_PAGE = '?paged=2'

TEST_PODCAST = {
    'feed_url': 'http://example.com/feed',
    'title': 'Test Feed',
    'itunes_type': 'serial',
}
TEST_EPISODE = {
    'title': 'Le fancey episode',
    'guid': 'http://example.com/feed/01-testep',
    'media_url': 'http://example.com/feed/01-testep.mp3',
    'published': datetime(2018, 3, 12, 10, tzinfo=timezone.utc),
}


class UtilFunctionsTestCase(TestCase):
    pass


class PodcastModelTestCase(TestCase):
    def setUp(self):
        Podcast.objects.create(feed_url=TEST_FEED)

    def test_podcast_model(self):
        """Test creation of Podcast model from different inputs"""
        podcast = Podcast.objects.get(feed_url=TEST_FEED)
        self.assertEqual(podcast.title, '')

        with self.assertRaises(IntegrityError):
            Podcast.objects.create_from_feed_url(TEST_FEED)

        with self.assertLogs('podcasts.models', level='INFO') as logs:
            podcast.update()
            self.assertEqual(podcast.title, 'Killing Time')

        self.assertIn('INFO:podcasts.models.podcast:Fetched Killing Time', logs.output[0])
        self.assertEqual(logs.output[1:], ['INFO:podcasts.models.podcast:Inserting cover image',
                                           'INFO:podcasts.models.podcast:Inserting episodes from first page',
                                           'INFO:podcasts.models.podcast:No next page found',
                                           'INFO:podcasts.models.podcast:All done', ])

        self.assertEqual(podcast.get_absolute_url(), '/podcasts/killing-time/')

        # get_or_create should return the same podcast now
        same_one, created = Podcast.objects.get_or_create_from_feed_url(TEST_FEED)
        self.assertEqual(podcast, same_one)
        self.assertFalse(created)

        # Should have more than 0 episodes
        self.assertGreaterEqual(Episode.objects.count(), 0)

        # Deletion should remove Podcast and cascade to Episodes
        podcast.delete()
        self.assertEqual(Podcast.objects.count(), 0)
        self.assertEqual(Episode.objects.count(), 0)

        # Create complete Podcast from feed_url, with pages
        with self.assertLogs('podcasts.models', level='INFO') as logs:
            podcast, created = Podcast.objects.get_or_create_from_feed_url(TEST_FEED_PAGED)
            self.assertTrue(created)
            self.assertTrue(isinstance(podcast, Podcast))

        self.assertIn('INFO:podcasts.models.podcast:Fetched CRE', logs.output[0])
        self.assertEqual(logs.output[1:4], ['INFO:podcasts.models.podcast:Inserting cover image',
                                            'INFO:podcasts.models.podcast:Inserting episodes from first page',
                                            'INFO:podcasts.models.podcast:Fetching next page %s%s ...' %
                                            (TEST_FEED_PAGED, TEST_FEED_PAGED_SECOND_PAGE), ])
        self.assertEqual(logs.output[-2:], ['INFO:podcasts.models.podcast:No next page found',
                                            'INFO:podcasts.models.podcast:All done', ])

        # Update Podcast, detection of existing episodes
        with self.assertLogs('podcasts.models', level='INFO') as logs:
            podcast.update(insert_cover=False)

        self.assertEqual(logs.output[1:], ['INFO:podcasts.models.podcast:Inserting episodes from first page',
                                           'INFO:podcasts.models.podcast:Found existing episodes',
                                           'INFO:podcasts.models.podcast:All done', ])


class FilenameCreationTestCase(TestCase):
    valid_naming_scheme = '$podcast_type/$podcast_slug/${episode_date}_$episode_title'
    invalid_naming_scheme = '$podcast_type/${podcast_slug}_$episode_testattr'
    datefmt = 'Y-m-d_Hi'

    def setUp(self):
        self.podcast = Podcast.objects.create(**TEST_PODCAST)
        self.episode = self.podcast.episodes.create(**TEST_EPISODE)

    def test_valid_call(self):
        """Check everything's fine with a valid naming scheme"""
        should_be = 'serial/test-feed/2018-03-12_1000_Le fancey episode.mp3'

        file_path = self.episode.construct_file_path('', self.valid_naming_scheme, self.datefmt)
        self.assertEqual(file_path, should_be)

    def test_invalid_segment(self):
        """Check that an invalid segments is untouched"""
        should_be = 'serial/test-feed_$episode_testattr.mp3'
        file_path = self.episode.construct_file_path('', self.invalid_naming_scheme, self.datefmt)
        self.assertEqual(file_path, should_be)


class PodcastsSettingsModelTestCase(TestCase):
    def test_settings_model(self):
        site = Site.objects.create(name='Test Site', domain='testsite.local')

        # Creating a Site object, fires a post_save creation of PodcastsSettings
        # therefore trying to create another PS object with the same Site should
        # cause the unique constraint to kick in
        with self.assertRaises(IntegrityError):
            PodcastsSettings.objects.create(site=site)

        # OneToOne rel should contain the PS instance
        settings = site.podcastssettings
        self.assertIsInstance(settings, PodcastsSettings)

        # Return the proper __str__ based on the Site.name
        self.assertEqual(str(settings), 'Test Site Podcasts Settings')


class EpisodeModelTestCase(TestCase):
    def setUp(self):
        self.podcast = Podcast.objects.create(feed_url=TEST_FEED)
        self.podcast.update()

    def test_episode_model(self):

        # Episode object cannot be created empty (requires GUID and Podcast)
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                episode = Episode.objects.create()
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                episode = Episode.objects.create(guid='testguid')

        with transaction.atomic():
            episode = Episode.objects.create(
                guid='/testguid1/',
                podcast=self.podcast,
            )
        self.assertEqual(str(episode), 'Killing Time\'s Episode')


        with transaction.atomic():
            episode = Episode.objects.create(
                guid='/testguid2/',
                podcast=self.podcast,
                title='Fancy Test Episode',
            )
        self.assertEqual(str(episode), 'Fancy Test Episode')

        # episode = Episode.objects.create()
