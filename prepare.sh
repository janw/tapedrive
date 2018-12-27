#!/bin/bash
set -e

# Django setup tasks
echo "Compiling messages."
python manage.py compilemessages

echo "Compiling and collecting static files"
webpack --mode production
python manage.py collectstatic --no-input -v0 --ignore "src"
