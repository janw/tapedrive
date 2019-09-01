from django.db.models.functions import Lower

from rest_framework import viewsets
from rest_framework import renderers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics

from requests import HTTPError, ConnectionError

from podcasts.models.podcast import Podcast
from podcasts.models.episode import Episode
from podcasts.api import serializers


class PodcastViewSet(viewsets.ModelViewSet):

    queryset = Podcast.objects.order_by(Lower("title"))
    serializer_class = serializers.PodcastSerializer
    list_serializer_class = serializers.PodcastListSerializer
    lookup_field = "slug"

    def get_serializer_class(self):
        if self.action == "list":
            return self.list_serializer_class
        return self.serializer_class

    def get_queryset(self, *args, **kwargs):
        if self.action == "list":
            return self.queryset.filter(subscribers=self.request.user)
        return self.queryset

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
            try:
                podcast, created = Podcast.objects.get_or_create_from_feed_url(
                    serializer.data["feed_url"], subscriber=request.user
                )
            except HTTPError as exc:
                return Response(serializer.data, status=exc.response.status_code)

            data = self.serializer_class(podcast, context={"request": request}).data
            data["created_now"] = created
            return Response(data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EpisodeViewSet(viewsets.ModelViewSet):
    queryset = Episode.objects.all()
    serializer_class = serializers.EpisodeSerializer
    list_serializer_class = serializers.EpisodeListSerializer

    def get_queryset(self, *args, **kwargs):
        if self.action == "list":
            return self.queryset.order_by("-published", "title")
        return self.queryset

    def get_serializer_class(self):
        if self.action == "list":
            return self.list_serializer_class
        return self.serializer_class

    @action(detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
    def shownotes(self, request, *args, **kwargs):
        episode = self.get_object()
        return Response(episode.shownotes)


class PodcastEpisodesList(generics.ListAPIView):
    serializer_class = serializers.EpisodeInlineSerializer

    def get_queryset(self):
        slug = self.kwargs["slug"]
        return Episode.objects.filter(podcast__slug=slug).order_by("-published")
