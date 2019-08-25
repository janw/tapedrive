from os import environ
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)

User = get_user_model()


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        if User.objects.count() == 0:
            username = "admin"
            email = "changeme@tapedrive.io"
            password = environ.get("INITIAL_ADMIN_PASSWORD", "admin")
            logger.info("Creating initial admin account.")
            admin = User.objects.create_superuser(
                email=email, username=username, password=password
            )
            admin.is_active = True
            admin.is_admin = True
            admin.save()
