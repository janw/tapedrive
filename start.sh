#!/usr/bin/env bash

export DJANGO_CONFIGURATION=Production

# Start Gunicorn processes
echo Starting Gunicorn.
exec gunicorn podcastarchive.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3
