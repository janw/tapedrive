# Generated by Django 2.0.5 on 2018-05-31 21:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('podcasts', '0004_listener_dark_mode'),
    ]

    operations = [
        migrations.AddField(
            model_name='episode',
            name='shownotes',
            field=models.TextField(blank=True, null=True, verbose_name='Show Notes'),
        ),
    ]
