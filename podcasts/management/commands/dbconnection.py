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
        print("Waiting for Database connection.")
        retry_count = 30
        while retry_count > 0:
            try:
                connection.ensure_connection()
            except Exception:
                print(".", end="")
                time.sleep(1)
                retry_count -= 1
            else:
                print()
                sys.exit(0)
        print("\nDatabase did not become available in time.")
        sys.exit(1)
