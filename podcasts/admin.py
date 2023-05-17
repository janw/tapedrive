from django.contrib import admin

from podcasts.models.episode import Episode, EpisodePlaybackState
from podcasts.models.podcast import Podcast


# Register your models here.
@admin.register(Podcast)
class PodcastAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "fetched", "updated")
    pass


class PlaybackStateInline(admin.TabularInline):
    model = EpisodePlaybackState


@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    list_display = ("title", "podcast", "published", "guid")
    readonly_fields = ("media_url", "link", "guid", "slug")

    inlines = [PlaybackStateInline]
