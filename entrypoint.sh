#!/bin/sh
set -eux

mkdir -p logs

echo "Running migrations..."
python manage.py migrate --noinput

echo "Running collectstatic..."
python manage.py collectstatic --noinput

echo "Creating or updating superuser..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
username = 'egemen'
password = 'Egemen32!'  # Buraya istediğin şifreyi yaz
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email='tuglacihukuk@gmail.com', password=password)
else:
    user = User.objects.get(username=username)
    user.set_password(password)
    user.save()
"

echo "Starting Gunicorn..."
exec gunicorn mywebsite.wsgi:application --bind 0.0.0.0:${PORT:-8001}
