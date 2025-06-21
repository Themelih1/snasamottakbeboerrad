#!/bin/sh
set -eux

mkdir -p logs

echo "Running migrations..."
python manage.py migrate --noinput

echo "Running collectstatic..."
python manage.py collectstatic --noinput

echo "Running compress..."
python manage.py compress --force

echo "Starting Gunicorn..."
exec gunicorn mywebsite.wsgi:application --bind 0.0.0.0:${PORT:-8001}
