#!/bin/bash
set -e

echo "Waiting for database to be ready..."
sleep 5

echo "Running migrations..."
python manage.py migrate --no-input

echo "Collecting static files..."
python manage.py collectstatic --no-input

# Create default superuser if it doesn’t exist
echo "Creating default admin user..."
python manage.py shell -c "from deployment.create_admin_user import *"

echo "Starting Gunicorn..."
exec gunicorn socialnet_mono.wsgi:application -c deployment/gunicorn.conf.py
