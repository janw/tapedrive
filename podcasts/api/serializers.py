from podcasts.models.podcast import Podcast
from podcasts.models.episode import Episode
from podcasts.models import EpisodeChapter
from background_task.models import Task
from rest_framework import serializers


class PodcastSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Podcast
        fields = "__all__"


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
