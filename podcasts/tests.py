from django.test import TestCase
from django.db.utils import IntegrityError
from podcasts.models.podcast import Podcast
# Create your tests here.

TEST_FEED = 'http://feeds.5by5.tv/killingtime'


class UtilFunctionsTestCase(TestCase):
    pass


class PodcastModelTestCase(TestCase):
    def setUp(self):
        Podcast.objects.create(feed_url=TEST_FEED)

    def test_podcast_model(self):
        """Test that the Podcast model is created and updated properly from all angles"""
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
