# Generated by Django 2.2.4 on 2019-09-01 11:20

from django.db import migrations, models
import podcasts.models.episode


class Migration(migrations.Migration):

    dependencies = [("podcasts", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="episode",
            name="image",
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to=podcasts.models.common.cover_image_filename,
                verbose_name="Cover Image",
            ),
        )
    ]
