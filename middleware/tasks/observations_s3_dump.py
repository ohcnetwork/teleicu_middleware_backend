import logging
from datetime import datetime

from celery import shared_task
from django.conf import settings

from middleware.observation.types import DataDumpRequest, MonitorOptions
from middleware.observation.utils import get_data_for_s3_dump, make_data_dump_to_s3

logger = logging.getLogger(__name__)


@shared_task
def observations_s3_dump():
    data = get_data_for_s3_dump()
    if not data:
        logger.info("No observation data found for S3 dump.")
        return
    make_data_dump_to_s3(
        request=DataDumpRequest(
            data=data,
            key=f"{settings.HOST_NAME}/{datetime.now()}.json",
            monitor_options=MonitorOptions(
                slug="s3_observations_dump",
                options={
                    "schedule": {
                        "type": "crontab",
                        "value": "30 * * * *",
                    },
                },
            ),
        )
    )
