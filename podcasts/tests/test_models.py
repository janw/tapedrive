from django.test import TestCase
from django.db import transaction
from django.db.utils import IntegrityError
from podcasts.models.episode import Episode
from podcasts.models.podcast import Podcast
from podcasts.models import PodcastsSettings
from django.contrib.sites.models import Site
# Create your tests here.

TEST_FEED = 'http://feeds.5by5.tv/killingtime'


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

        podcast.update()
        self.assertEqual(podcast.title, 'Killing Time')

        podcast2, created = Podcast.objects.get_or_create_from_feed_url(TEST_FEED)
        self.assertEqual(podcast, podcast2)
        self.assertFalse(created)

        podcast.delete()
        podcast, created = Podcast.objects.get_or_create_from_feed_url(TEST_FEED)
        self.assertTrue(created)

        self.assertEqual(str(podcast), 'Killing Time')
        self.assertEqual(podcast.get_absolute_url(), '/podcasts/killing-time/')

        podcast.create_episodes()

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

        # settings"%s Podcasts Settings" % self.site


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
