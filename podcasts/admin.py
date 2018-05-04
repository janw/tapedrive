from django.contrib import admin
from .models import Podcast, Episode, EpisodePlaybackState


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
