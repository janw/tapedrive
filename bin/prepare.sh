#!/bin/bash
set -e

# Django setup tasks
echo "Compiling messages."
python manage.py compilemessages

echo "Compiling and collecting static files"
./node_modules/webpack/bin/webpack.js --mode production
python manage.py collectstatic --no-input -v0 --ignore "src"
