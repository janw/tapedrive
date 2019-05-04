from podcasts.models.episode import Episode
from podcasts.models.podcast import Podcast
from podcasts.models import EpisodeChapter
from podcasts import conf

from rest_framework import serializers


class PodcastSerializer(serializers.ModelSerializer):
    class Meta:
        model = Podcast
        fields = "__all__"


class EpisodeChapterSerializer(serializers.ModelSerializer):
    class Meta:
        model = EpisodeChapter
        fields = ("starttime", "title", "link", "image")


class EpisodeSerializer(serializers.ModelSerializer):
    chapters = EpisodeChapterSerializer(many=True, read_only=True)
    podcast = PodcastSerializer(read_only=True)

    class Meta:
        model = Episode
        fields = "__all__"


class ApplePodcastsSearchRequestSerializer(serializers.Serializer):
    term = serializers.CharField(trim_whitespace=True, min_length=3)
    media = serializers.CharField(default="podcast", read_only=True)
    limit = serializers.IntegerField(default=conf.ITUNES_SEARCH_LIMIT, read_only=True)
