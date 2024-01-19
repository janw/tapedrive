import os
from io import BytesIO

from django.core.files import File
from django.db import models
from django.utils.translation import gettext as _

from podcasts import utils


def chapter_image_filename(instance, filename):
    ext = os.path.splitext(filename)[-1]

    filename = f"{instance.episode.podcast.slug}-{instance.episode.pk}-{instance.pk}"
    return filename + ext


class EpisodeChapter(models.Model):
    episode = models.ForeignKey(
        "podcasts.Episode",
        on_delete=models.CASCADE,
        related_name="old_chapters",
        verbose_name=_("Episode of Chapter"),
    )
    starttime = models.DurationField(
        blank=False,
        null=False,
        verbose_name=_("Chapter Start"),
    )
    title = models.CharField(
        blank=False,
        null=False,
        max_length=2047,
        verbose_name=_("Chapter Title"),
    )
    link = models.URLField(
        blank=True,
        default="",
        max_length=2047,
        verbose_name=_("Chapter Link"),
    )
    image_url = models.URLField(
        blank=True,
        default="",
        max_length=2047,
        verbose_name=_("Chapter Image URL"),
    )
    image = models.ImageField(
        blank=True,
        null=True,
        upload_to=chapter_image_filename,
        verbose_name=_("Chapter Image"),
    )

    class Meta:
        verbose_name = _("Episode")
        verbose_name_plural = _("Episodes")
        ordering = ["starttime"]

    def __str__(self) -> str:
        return f"{self.title} of episode {self.episode_id}"

    def save(self, *args, **kwargs):
        if not self.image:
            self.insert_image(self.image_url)
        super().save(*args, **kwargs)

    def insert_image(self, img_url=None):
        if img_url:
            self.image_url = img_url
        else:
            img_url = self.image_url

        if img_url:
            output = BytesIO()
            name = utils.download_cover(img_url, output)
            if name:
                self.image.save(name, File(output), save=True)
