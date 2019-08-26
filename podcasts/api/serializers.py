from podcasts.models.podcast import Podcast
from podcasts.models.episode import Episode
from podcasts.models import EpisodeChapter
from background_task.models import Task
from rest_framework import serializers


class PodcastSerializer(serializers.HyperlinkedModelSerializer):
    episodes = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

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


class PodcastFromUrlSerializer(serializers.ModelSerializer):
    class Meta:
        model = Podcast
        fields = ("feed_url",)


class EpisodeChapterSerializer(serializers.ModelSerializer):
    class Meta:
        model = EpisodeChapter
        fields = ("starttime", "title", "link", "image")


class EpisodeDownloadTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ("task_hash", "run_at", "attempts", "failed_at")


class EpisodeSerializer(serializers.HyperlinkedModelSerializer):
    chapters = EpisodeChapterSerializer(many=True, read_only=True)
    podcast = PodcastSerializer(read_only=True)
    download_task = EpisodeDownloadTaskSerializer(read_only=True)

    class Meta:
        model = Episode
        fields = "__all__"
