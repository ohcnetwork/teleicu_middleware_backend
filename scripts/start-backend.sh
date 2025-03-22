#!/bin/bash

python manage.py collectstatic --noinput --clear

daphne -b 0.0.0.0 -p 8090 core.asgi:application
