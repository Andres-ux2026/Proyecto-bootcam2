#!/usr/bin/env bash
set -e

python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py seed_data

gunicorn ecommerce.wsgi:application --bind 0.0.0.0:$PORT
