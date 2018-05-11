from django.contrib import admin
from podcasts.models.podcast import Podcast
from podcasts.models.episode import Episode
from podcasts.models.listener import EpisodePlaybackState


# Register your models here.
@admin.register(Podcast)
class PodcastAdmin(admin.ModelAdmin):
    # fields = ('title', )
    pass


class PlaybackStateInline(admin.TabularInline):
    model = EpisodePlaybackState


@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    list_display = ('title', 'podcast', 'published')
    readonly_fields = ('media_url', 'link', 'guid')

    inlines = [
        PlaybackStateInline,
    ]
