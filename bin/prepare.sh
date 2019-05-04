#!/bin/bash
set -e

# Setup front-end stuff
npm update
"`npm bin`/webpack" --mode production


# Django setup tasks
echo "Compiling messages."
python manage.py compilemessages

echo "Compiling and collecting static files"
python manage.py collectstatic --no-input -v0 --ignore "src"
