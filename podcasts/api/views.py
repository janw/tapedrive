from rest_framework import viewsets
from rest_framework import renderers
from rest_framework.decorators import action
from rest_framework.response import Response

from podcasts.models.podcast import Podcast
from podcasts.models.episode import Episode
from podcasts.api import serializers


class PodcastViewSet(viewsets.ModelViewSet):

    queryset = Podcast.objects.all()
    serializer_class = serializers.PodcastSerializer
    lookup_field = "slug"

    def get_queryset(self, *args, **kwargs):
        return self.queryset.filter(subscribers=self.request.user)

    @action(detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
    def summary(self, request, *args, **kwargs):
        podcast = self.get_object()
        return Response(podcast.summary_p)

    def perform_create(self, serializer):
        instance = serializer.save()
        self.request.user.subscribed_podcasts.add(instance)


class EpisodeViewSet(viewsets.ModelViewSet):

    queryset = Episode.objects.all()
    serializer_class = serializers.EpisodeSerializer
