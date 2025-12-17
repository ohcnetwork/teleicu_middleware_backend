#!/bin/bash

python manage.py collectstatic --noinput --clear

echo "starting server..."
if [[ "${ATTACH_DEBUGGER}" == "true" ]]; then
  echo "waiting for debugger..."
  python -m debugpy --wait-for-client --listen 0.0.0.0:9876 manage.py runserver 0.0.0.0:8090
else
  python manage.py runserver 0.0.0.0:8090
fi
