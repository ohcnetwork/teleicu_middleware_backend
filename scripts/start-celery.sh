#!/bin/bash

# Run migrations
python manage.py migrate
python manage.py collectstatic --noinput

# Start Celery worker
celery -A middleware.celery worker -B --loglevel=info
