#!/bin/bash

# Run migrations
python manage.py migrate

# Start Celery worker
celery -A core.celery_app worker -B --loglevel=info
