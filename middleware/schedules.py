from celery import current_app
from celery.schedules import crontab

from middleware.tasks import (
    automated_daily_rounds,
    observations_s3_dump,
    retrieve_asset_config,
    store_camera_statuses,
)


@current_app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    # Run retrieve_asset_config every minute
    sender.add_periodic_task(
        crontab(minute="*"),
        retrieve_asset_config.s(),
        name="run-retrieve-asset-config",
    )

    # Run automated_daily_rounds every hour
    sender.add_periodic_task(
        crontab(minute="0"),
        automated_daily_rounds.s(),
        name="run-automated-daily-round",
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
