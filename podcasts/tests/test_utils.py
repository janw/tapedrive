from django.test import TestCase
from podcasts import utils

TEST_FEED = 'https://raw.githubusercontent.com/janw/tapedrive/master/.testdata/valid.xml'
TEST_FEED_NONEXISTENT = 'http://localhost/nonexistent'
TEST_FEED_HTTPERROR = 'https://raw.githubusercontent.com/janw/tapedrive/master/.testdata/literally_nonexistent.xml'
TEST_FEED_MALFORMED = 'https://raw.githubusercontent.com/janw/tapedrive/master/.testdata/invalid.xml'
TEST_FEED_NEXT_PAGE = 'https://raw.githubusercontent.com/janw/tapedrive/master/.testdata/paged_p1.xml'
TEST_FEED_SUBTITLE_TOO_LONG = 'https://raw.githubusercontent.com/janw/tapedrive/master/.testdata/subtitle_too_long.xml'


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
