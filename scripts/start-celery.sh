#!/bin/bash

# Run migrations
python manage.py migrate

# Start Celery worker
celery -A core.celery worker -B --loglevel=info
