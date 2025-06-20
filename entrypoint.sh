#!/bin/sh
set -eux

mkdir -p logs

echo "Running migrations..."
python manage.py migrate --noinput

echo "Creating admin user if not exists..."
python manage.py shell -c "
from django.contrib.auth.models import User;
username = 'egemen';
email = 'tuglacihukuk@gmail.com';
password = 'Egemen4004!';
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print('Admin user created.')
else:
    print('Admin user already exists.')
"

echo "Running collectstatic..."
python manage.py collectstatic --noinput

echo "Starting Gunicorn..."
exec gunicorn mywebsite.wsgi:application --bind 0.0.0.0:${PORT:-8001}
