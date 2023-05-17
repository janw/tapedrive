import logging
import sys
import time

from django.core.management.base import BaseCommand
from django.db import connection

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Wait for a usable database connection."

    def handle(self, *args, **options):
        # If connection is already up: exit.
        if connection.connection is not None:
            sys.exit(0)

        # Wait for a proper database connection
        logger.info("Waiting for Database connection.")
        retry_count = 30
        while retry_count > 0:
            try:
                connection.ensure_connection()
            except Exception:
                time.sleep(1)
                retry_count -= 1
            else:
                sys.exit(0)
        logger.error(f"Database did not become available in {retry_count} seconds.")
        sys.exit(1)
