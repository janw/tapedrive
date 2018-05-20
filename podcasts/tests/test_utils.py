from django.test import TestCase
from podcasts import utils
from podcasts.models.podcast import Podcast
from datetime import datetime, timezone

TEST_FEED = 'http://feeds.5by5.tv/killingtime'
TEST_FEED_NONEXISTENT = 'http://localhost/killingnothing'
TEST_FEED_HTTPERROR = 'https://github.com/janwh/nonexistenturl'
TEST_FEED_MALFORMED = 'https://raw.githubusercontent.com/kurtmckee/feedparser/develop/tests/illformed/aaa_illformed.xml'
TEST_FEED_NEXT_PAGE = 'http://cre.fm/feed/m4a'
TEST_FEED_SUBTITLE_TOO_LONG = 'https://rss.art19.com/caliphate'

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


class ResolveSegmentsTestCase(TestCase):
    string = '{podcast_segments}||{episode_segments}||{unifying_segments}'

    def test_valid_help_string(self):
        should_become = ('<code>$podcast_slug</code>, <code>$podcast_type</code>, <code>$podcast_title</code>, <code>$p'
                         'odcast_subtitle</code>, <code>$podcast_author</code>, <code>$podcast_language</code>, <code>$'
                         'podcast_explicit</code>, <code>$podcast_updated</code>||<code>$episode_slug</code>, <code>$ep'
                         'isode_id</code>, <code>$episode_date</code>, <code>$episode_number</code>, <code>$episode_typ'
                         'e</code>, <code>$episode_title</code>||<code>$episode_slug</code>, <code>$episode_id</code>, '
                         '<code>$episode_date</code>, <code>$episode_number</code>, <code>$episode_title</code>')
        self.assertEqual(utils.resolve_segments(self.string), should_become)


class FeedRefreshTestCase(TestCase):

    def test_valid_feed(self):
        feed_info = utils.refresh_feed(TEST_FEED)
        self.assertIsNotNone(feed_info)
        self.assertEqual(feed_info.data['title'], 'Killing Time')

    def test_various_feeds(self):
        """Querying an invalid feed should always fail softly, returning None"""
        with self.assertLogs('podcasts.utils', level='INFO') as logs:
            feed_info = utils.refresh_feed(TEST_FEED_NONEXISTENT)
            self.assertIsNone(feed_info)

            feed_info = utils.refresh_feed(TEST_FEED_HTTPERROR)
            self.assertIsNone(feed_info)

            feed_info = utils.refresh_feed(TEST_FEED_MALFORMED)
            self.assertIsNone(feed_info)

            feed_info = utils.refresh_feed(TEST_FEED_NEXT_PAGE)
            self.assertIsNotNone(feed_info.next_page)

        self.assertEqual(logs.output, ['ERROR:podcasts.utils:Connection error',
                                       'ERROR:podcasts.utils:HTTP error 404: Not Found',
                                       'ERROR:podcasts.utils:Feed is malformatted',
                                       'INFO:podcasts.utils:Feed has next page'])

    def test_long_subtitle_feed(self):
        """Test if an overly long subtitle is properly truncated"""
        with self.assertLogs('podcasts.utils', level='INFO') as logs:
            feed_info = utils.refresh_feed(TEST_FEED_SUBTITLE_TOO_LONG)
            self.assertTrue(len(feed_info.data['subtitle']) == 255)
            self.assertTrue(feed_info.data['subtitle'].endswith(' ...'))

        self.assertEqual(logs.output, ['WARNING:podcasts.utils:Subtitle too long, will be truncated', ])
