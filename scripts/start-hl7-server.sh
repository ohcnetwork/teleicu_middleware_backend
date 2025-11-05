#!/bin/bash

python manage.py collectstatic --noinput --clear -v0


python core/mllp_server.py
