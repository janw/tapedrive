from django.test import TestCase
from podcasts import utils
from podcasts.models.podcast import Podcast
from datetime import datetime, timezone

TEST_FEED = 'http://feeds.5by5.tv/killingtime'
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
        should_become = ('<span>{podcast_slug}</span>, <span>{podcast_type}</span>, <span>{podcast_title}</span>, ' +
        '<span>{podcast_subtitle}</span>, <span>{podcast_author}</span>, <span>{podcast_language}</span>, ' +
        '<span>{podcast_explicit}</span>, <span>{podcast_updated}</span>||<span>{episode_slug}</span>, ' +
        '<span>{episode_id}</span>, <span>{episode_date}</span>, <span>{episode_number}</span>, ' +
        '<span>{episode_type}</span>, <span>{episode_title}</span>||<span>{episode_slug}</span>, ' +
        '<span>{episode_id}</span>, <span>{episode_date}</span>, <span>{episode_number}</span>, ' +
        '<span>{episode_title}</span>')
        self.assertEqual(utils.resolve_segments(self.string), should_become)

    def test_changed_wrapper(self):
        should_become = ('<code>{podcast_slug}</code>, <code>{podcast_type}</code>, <code>{podcast_title}</code>, ' +
        '<code>{podcast_subtitle}</code>, <code>{podcast_author}</code>, <code>{podcast_language}</code>, ' +
        '<code>{podcast_explicit}</code>, <code>{podcast_updated}</code>||<code>{episode_slug}</code>, ' +
        '<code>{episode_id}</code>, <code>{episode_date}</code>, <code>{episode_number}</code>, ' +
        '<code>{episode_type}</code>, <code>{episode_title}</code>||<code>{episode_slug}</code>, ' +
        '<code>{episode_id}</code>, <code>{episode_date}</code>, <code>{episode_number}</code>, ' +
        '<code>{episode_title}</code>')
        self.assertEqual(utils.resolve_segments(self.string, wrap_in='code'), should_become)


class FilenameCreationTestCase(TestCase):
    valid_naming_scheme = '{podcast_type}/{podcast_slug}/{episode_date}_{episode_title}'

    def setUp(self):
        self.podcast = Podcast.objects.create(**TEST_PODCAST)
        self.episode = self.podcast.episodes.create(**TEST_EPISODE)

    def test_valid_call(self):
        should_be = 'serial/test-feed/2018-03-12 10:00:00+00:00_Le fancey episode'
        filename = utils.construct_download_filename(self.valid_naming_scheme, self.episode)
        self.assertEqual(filename, should_be)
