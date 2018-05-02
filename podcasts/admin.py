from django.contrib import admin
from .models import Podcast, Episode


# Register your models here.
@admin.register(Podcast)
class PodcastAdmin(admin.ModelAdmin):
    # fields = ('title', )
    pass
