from django.apps import apps
from django.core.management.base import BaseCommand

from podcasts.utils import refresh_feed

import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "My shiny new management command."

    # def add_arguments(self, parser):
        # parser.add_argument('--verbosity', type=int)

    def handle(self, *args, **options):
        verbosity = int(options['verbosity'])
        root_logger = logging.getLogger('')
        if verbosity > 1:
            root_logger.setLevel(logging.DEBUG)

        logger.debug("I'm doing something")

        Podcast = apps.get_model('podcasts', 'Podcast')

        for podcast in Podcast.objects.iterator():
            logger.info('Refreshing feed: %s ...' % podcast.title)

            info = refresh_feed(podcast.feed_url)
            logger.debug('Received ...')

            podcast.create_episodes(info)

        # raise NotImplementedError()
