from os import path
from io import BytesIO

from django.db import models

from podcasts.utils import download_cover


def cover_image_filename(instance, filename):
    ext = path.splitext(filename)[-1]
    return f"{instance.__class__.__name__.lower()}-{instance.id}-cover{ext}"


class CommonAbstract(models.Model):
    class Meta:
        abstract = True

    image = models.ImageField(
        blank=True,
        null=True,
        upload_to=cover_image_filename,
        verbose_name="Cover Image",
    )

    def insert_cover(self, img_url):
        if img_url:
            file = download_cover(img_url)
            if file:
                self.image.save(file.name, file, save=True)
