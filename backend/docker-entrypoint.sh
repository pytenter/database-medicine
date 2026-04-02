#!/bin/sh
set -e

cd /app/backend
python scripts/init_compose_db.py
python manage.py check
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 120
