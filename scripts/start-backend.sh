#!/bin/bash

python manage.py collectstatic --noinput

daphne -b 0.0.0.0 -p 8090 core.asgi:application
