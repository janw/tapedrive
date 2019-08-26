from rest_framework import viewsets
from rest_framework import renderers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from podcasts.models.podcast import Podcast
from podcasts.models.episode import Episode
from podcasts.api import serializers


class PodcastViewSet(viewsets.ModelViewSet):

    queryset = Podcast.objects.all()
    serializer_class = serializers.PodcastSerializer
    list_serializer_class = serializers.PodcastListSerializer
    lookup_field = "slug"

    def get_serializer_class(self):
        if self.action == "list":
            return self.list_serializer_class
        return self.serializer_class

    def get_queryset(self, *args, **kwargs):
        return self.queryset.filter(subscribers=self.request.user)

    @action(detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
    def summary(self, request, *args, **kwargs):
        podcast = self.get_object()
        return Response(podcast.summary_p)

    def perform_create(self, serializer):
        instance = serializer.save()
        self.request.user.subscribed_podcasts.add(instance)

    @action(detail=False, methods=["post"])
    def add(self, request):
        serializer = serializers.PodcastFromUrlSerializer(data=request.data)
        if serializer.is_valid():
            podcast, created = Podcast.objects.get_or_create_from_feed_url(
                serializer.data["feed_url"]
            )
            podcast.subscribers.add(request.user)
            data = self.serializer_class(podcast, context={"request": request}).data
            if created:
                return Response(data, status=status.HTTP_201_CREATED)
            return Response(data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EpisodeViewSet(viewsets.ModelViewSet):

    queryset = Episode.objects.all()
    serializer_class = serializers.EpisodeSerializer
