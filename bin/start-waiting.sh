#!/bin/bash
set -e

echo "Waiting for Database connection "
until python manage.py dbconnection 2> /dev/null
do
  printf "."
  sleep 1
done

echo -e "\nDatabase ready."
exec ./start.sh
