from django.core.management.base import BaseCommand
from django.db import connection
import logging
import sys
import time

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Wait for a usable database connection."

    def handle(self, *args, **options):

        # If connection is already up: exit.
        if connection.connection is not None:
            sys.exit(0)

        # Wait for a proper database connection
        while True:
            try:
                connection.ensure_connection()
            except Exception:
                print('Connection to database cannot be established.')
                time.sleep(1)
            else:
                sys.exit(0)
