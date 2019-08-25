#!/bin/sh
set -e

python manage.py dbconnection
python manage.py migrate
python manage.py initadmin

echo "Starting main process."
exec $@
