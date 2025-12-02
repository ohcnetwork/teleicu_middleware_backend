from celery import current_app
from celery.schedules import crontab
from django.conf import settings

from middleware.tasks.automated_observations import automated_observations
from middleware.tasks.observations_s3_dump import observations_s3_dump
from middleware.tasks.store_camera_statuses import store_camera_statuses


@current_app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    # Run automated observations every hour
    sender.add_periodic_task(
        settings.AUTOMATED_OBSERVATIONS_INTERVAL * 60,
        automated_observations.s(),
        name="run-automated-observations",
    )

    # Run observations_s3_dump every 30 seconds
    sender.add_periodic_task(
        30.0,
        observations_s3_dump.s(),
        name="dump-observations-to-s3",
    )

    # Run store_camera_statuses every minute
    sender.add_periodic_task(
        crontab(minute="*"),
        store_camera_statuses.s(),
        name="store-camera-statuses",
    )
