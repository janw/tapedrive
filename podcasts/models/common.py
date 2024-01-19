import itertools
from os import path

from django.db import models
from django.template.defaultfilters import slugify

from podcasts.utils import download_cover


def cover_image_filename(instance, filename):
    ext = path.splitext(filename)[-1]
    return f"{instance.__class__.__name__.lower()}-{instance.id}-cover{ext}"


class CommonAbstract(models.Model):
    image = models.ImageField(
        blank=True,
        null=True,
        upload_to=cover_image_filename,
        verbose_name="Cover Image",
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        # Update the slug, ensuring it's unique
        Model = self._meta.concrete_model
        if not self.id or not self.slug:
            max_length = self._meta.get_field("slug").max_length
            self.slug = orig = slugify(self.title)
            for x in itertools.count(1):
                if not Model.objects.filter(slug=self.slug).exists():
                    break
                self.slug = "%s-%d" % (orig[: max_length - len(str(x)) - 1], x)

            # Some items have ridiculously long titles, shorten to max slug length
            if len(self.slug) > max_length:
                self.slug = self.slug[:max_length]
            if self.slug.endswith("-"):
                self.slug = self.slug[:-1]

        super().save(*args, **kwargs)

    def insert_cover(self, img_url):
        if img_url:
            file = download_cover(img_url)
            if file:
                self.image.save(file.name, file, save=True)
