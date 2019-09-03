import logging

from django.apps import apps
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Refresh feeds of all podcasts in the database."

    def handle(self, *args, **options):
        verbosity = int(options["verbosity"])
        root_logger = logging.getLogger("")
        if verbosity > 1:
            root_logger.setLevel(logging.DEBUG)

        Podcast = apps.get_model("podcasts", "Podcast")
        for podcast in Podcast.objects.iterator():
            logger.info("Updating podcast feed: %s ..." % podcast.title)
            podcast.update()
            podcast.save()
