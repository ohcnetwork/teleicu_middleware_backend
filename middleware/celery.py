from __future__ import absolute_import, unicode_literals
import os

from celery import Celery
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "middleware.settings")

app = Celery("middleware")
app.config_from_object(settings, namespace="CELERY")


app.conf.enable_utc = False
app.conf.beat_schedule = {
    "run-me-every-ten-seconds": {
        "task": "middleware.tasks.test_celery_task",
        "schedule": 10.0,
    },
}

app.conf.beat_schedule = {
    "run-me-every-ten-seconds": {
        "task": "middleware.tasks.retrieve_asset_config",
        "schedule": 5.0,
    },
}

app.autodiscover_tasks()
