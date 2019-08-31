from podcasts.models.podcast import Podcast
from podcasts.models.episode import Episode
from podcasts.models import EpisodeChapter
from background_task.models import Task
from rest_framework import serializers


class EpisodeInlineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Episode
        fields = ("id", "title", "subtitle", "published", "downloaded")


class PodcastSerializer(serializers.HyperlinkedModelSerializer):
    num_episodes = serializers.IntegerField(read_only=True)
    last_published = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Podcast
        lookup_field = "slug"
        exclude = ("subscribers", "followers")
        extra_kwargs = {"url": {"lookup_field": "slug"}}


class PodcastListSerializer(serializers.ModelSerializer):
    num_episodes = serializers.IntegerField(read_only=True)
    last_published = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Podcast
        lookup_field = "slug"
        fields = (
            "title",
            "slug",
            "id",
            "subtitle",
            "image",
            "num_episodes",
            "last_published",
        )


class PodcastFromUrlSerializer(serializers.Serializer):
    feed_url = serializers.URLField()


class EpisodeChapterSerializer(serializers.ModelSerializer):
    class Meta:
        model = EpisodeChapter
        fields = ("starttime", "title", "link", "image")


class EpisodeDownloadTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ("task_hash", "run_at", "attempts", "failed_at")


class EpisodeSerializer(serializers.ModelSerializer):
    chapters = EpisodeChapterSerializer(many=True, read_only=True)
    download_task = EpisodeDownloadTaskSerializer(read_only=True)

    class Meta:
        model = Episode
        exclude = ("media_url",)
