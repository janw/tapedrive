#!/bin/bash
set -e

# Django setup tasks
echo "Setting up."
python manage.py migrate

# Start Honcho processes
echo "Starting Honcho."
exec honcho start
