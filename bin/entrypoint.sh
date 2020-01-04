#!/bin/sh
set -ex

# Collect static files from external apps
python manage.py collectstatic --no-input

# Check for database and migrate it
python manage.py dbconnection
python manage.py migrate

# Initialize admin account
python manage.py initadmin

echo "Starting main process."
exec $@
