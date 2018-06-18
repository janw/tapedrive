from podcasts.models.episode import Episode
from podcasts.models.podcast import Podcast
from podcasts.models import EpisodeChapter
from rest_framework import serializers


class PodcastSerializer(serializers.ModelSerializer):
    class Meta:
        model = Podcast
        fields = '__all__'


class EpisodeChapterSerializer(serializers.ModelSerializer):
    class Meta:
        model = EpisodeChapter
        fields = ('starttime', 'title', 'link', 'image')


class EpisodeSerializer(serializers.ModelSerializer):
    chapters = EpisodeChapterSerializer(many=True, read_only=True)
    podcast = PodcastSerializer(read_only=True)

    # MISSING:
    # object_dict['downloaded_fmt'] = _date(object.downloaded, get_format('DATETIME_FORMAT'))
    # object_dict['published_fmt'] = _date(object.published, get_format('DATETIME_FORMAT'))
    # object_dict['url_api_episode_queue_download'] = reverse('podcasts:api-episode-queue-download',
    #                                                         kwargs={'id': object.id})

    class Meta:
        model = Episode
        fields = '__all__'
