#!/bin/sh
set -ex

# Check for database and migrate it
python manage.py dbconnection
python manage.py migrate

# Initialize admin account
python manage.py initadmin

echo "Starting main process."
exec $@
