#!/bin/bash
set -e

# Django setup tasks
echo "Migrating Database."
python manage.py migrate

# Start Honcho processes
echo "Starting Honcho."
exec honcho start
