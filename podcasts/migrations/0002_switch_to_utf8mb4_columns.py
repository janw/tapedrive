# Generated by Django 2.0.5 on 2018-05-23 16:53

from django.db import migrations


def forwards(apps, schema_editor):
    if schema_editor.connection.vendor in ['sqlite', 'postgresql']:
        print('Not applicable due to DB vendor', schema_editor.connection.vendor)
        return
    with schema_editor.connection.cursor() as cursor:
        cursor.execute('ALTER TABLE podcasts_episode CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci')
        cursor.execute('ALTER TABLE podcasts_podcast CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci')


def reverses(apps, schema_editor):
    if schema_editor.connection.vendor in ['sqlite', 'postgresql']:
        print('Not applicable due to DB vendor', schema_editor.connection.vendor)
        return
    with schema_editor.connection.cursor() as cursor:
        cursor.execute('ALTER TABLE podcasts_episode CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci')
        cursor.execute('ALTER TABLE podcasts_podcast CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci')


class Migration(migrations.Migration):

    dependencies = [
        ('podcasts', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(forwards, reverses),
    ]