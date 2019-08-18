# Generated by Django 2.0.13 on 2019-08-18 09:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import podcasts.models
import podcasts.models.episode_chapter
import podcasts.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('sites', '0002_alter_domain_unique'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('background_task', '0002_auto_20170927_1109'),
    ]

    operations = [
        migrations.CreateModel(
            name='Episode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('guid', models.CharField(editable=False, max_length=255, unique=True, verbose_name='Episode GUID')),
                ('slug', models.SlugField(editable=False, max_length=255)),
                ('title', models.CharField(blank=True, max_length=255, null=True, verbose_name='Episode Title')),
                ('subtitle', models.CharField(blank=True, max_length=255, null=True, verbose_name='Episode Subtitle')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Episode Summary')),
                ('link', models.URLField(blank=True, null=True, verbose_name='Episode Link')),
                ('media_url', models.URLField(blank=True, editable=False, max_length=2047, null=True, verbose_name='Media URL')),
                ('published', models.DateTimeField(blank=True, null=True, verbose_name='Published')),
                ('downloaded', models.DateTimeField(blank=True, default=None, null=True, verbose_name='Downloaded')),
                ('itunes_duration', models.CharField(blank=True, max_length=32, null=True, verbose_name='Duration')),
                ('itunes_season', models.CharField(blank=True, max_length=32, null=True, verbose_name='Season')),
                ('itunes_episode', models.CharField(blank=True, max_length=32, null=True, verbose_name='Episode Number')),
                ('itunes_episodetype', models.CharField(blank=True, max_length=16, null=True, verbose_name='Episode Type')),
                ('file_originalname', models.CharField(blank=True, max_length=255, null=True, verbose_name='Original Filename')),
                ('file_path', models.FilePathField(blank=True, null=True, path='/data', recursive=True, verbose_name='File Location')),
                ('file_size', podcasts.models.BigPositiveIntegerField(blank=True, null=True, verbose_name='File Size')),
                ('file_sha256', models.CharField(blank=True, max_length=64, null=True, verbose_name='File Hash (SHA256)')),
                ('shownotes', models.TextField(blank=True, null=True, verbose_name='Show Notes')),
                ('download_task', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='background_task.Task', verbose_name='Associated Download Task')),
            ],
            options={
                'verbose_name': 'Episode',
                'verbose_name_plural': 'Episodes',
                'db_table': 'podcasts_episode',
            },
        ),
        migrations.CreateModel(
            name='EpisodeChapter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('starttime', models.DurationField(verbose_name='Chapter Start')),
                ('title', models.CharField(max_length=2047, verbose_name='Chapter Title')),
                ('link', models.URLField(blank=True, max_length=2047, null=True, verbose_name='Chapter Link')),
                ('image_url', models.URLField(blank=True, max_length=2047, null=True, verbose_name='Chapter Image URL')),
                ('image', models.ImageField(blank=True, null=True, upload_to=podcasts.models.episode_chapter.chapter_image_filename, verbose_name='Chapter Image')),
                ('episode', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chapters', to='podcasts.Episode', verbose_name='Episode of Chapter')),
            ],
            options={
                'verbose_name': 'Episode',
                'verbose_name_plural': 'Episodes',
                'ordering': ['starttime'],
            },
        ),
        migrations.CreateModel(
            name='EpisodePlaybackState',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.PositiveIntegerField(default=0, verbose_name='Playback Position')),
                ('completed', models.BooleanField(default=False, verbose_name='Playback Completed')),
                ('episode', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='playbackstates', to='podcasts.Episode')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='playbackstates', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Podcast',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='Untitled', max_length=255, verbose_name='Podcast Title')),
                ('subtitle', models.CharField(blank=True, max_length=255, null=True, verbose_name='Podcast Subtitle')),
                ('slug', models.SlugField(blank=True, editable=False, unique=True)),
                ('feed_url', models.URLField(unique=True, verbose_name='Feed URL')),
                ('added', models.DateTimeField(auto_now_add=True, verbose_name='Podcast Added')),
                ('fetched', models.DateTimeField(blank=True, null=True, verbose_name='Feed Fetched Last')),
                ('updated', models.DateTimeField(blank=True, null=True, verbose_name='Last Feed Update')),
                ('author', models.CharField(blank=True, max_length=255, null=True, verbose_name='Podcast Author')),
                ('language', models.CharField(blank=True, max_length=64, null=True, verbose_name='Main Language')),
                ('link', models.URLField(blank=True, max_length=64, null=True, verbose_name='Podcast Link')),
                ('image', models.ImageField(blank=True, null=True, upload_to=podcasts.models.cover_image_filename, verbose_name='Cover Image')),
                ('itunes_explicit', models.NullBooleanField(verbose_name='Explicit Tag')),
                ('itunes_type', models.CharField(blank=True, max_length=64, null=True, verbose_name='iTunes Type')),
                ('generator', models.CharField(blank=True, max_length=64, null=True, verbose_name='Feed Generator')),
                ('summary', models.TextField(blank=True, null=True, verbose_name='Podcast Summary')),
            ],
            options={
                'verbose_name': 'Podcast',
                'verbose_name_plural': 'Podcasts',
                'db_table': 'podcasts_podcast',
            },
        ),
        migrations.CreateModel(
            name='PodcastsSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('storage_directory', models.CharField(default='/data', help_text='Root directory of where the podcast episodes are downloaded to', max_length=255, validators=[podcasts.validators.validate_path], verbose_name='Storage Directory')),
                ('naming_scheme', models.CharField(default='$podcast_slug/$episode_slug', help_text='Scheme used to compile the episode download filenames', max_length=255, validators=[podcasts.validators.validate_naming_scheme], verbose_name='Episode Naming Scheme')),
                ('inpath_dateformat', models.CharField(default='Y-m-d_Hi', help_text='Scheme used to compile date segments in episode download filenames', max_length=255, verbose_name='In-Path Date Format')),
                ('site', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='sites.Site')),
            ],
            options={
                'verbose_name': 'Podcasts Settings',
                'verbose_name_plural': 'Podcasts Settings',
            },
        ),
        migrations.AddField(
            model_name='episode',
            name='podcast',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='episodes', to='podcasts.Podcast', verbose_name='Podcast'),
        ),
        migrations.AddField(
            model_name='episode',
            name='user',
            field=models.ManyToManyField(through='podcasts.EpisodePlaybackState', to=settings.AUTH_USER_MODEL, verbose_name="Episodes' Listeners"),
        ),
    ]
