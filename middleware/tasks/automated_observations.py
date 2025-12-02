import logging

from celery import shared_task

from middleware.care_client import CareClient
from middleware.observation.utils import (
    get_entries_for_automated_observations,
    get_static_observations,
)

logger = logging.getLogger(__name__)


@shared_task
def automated_observations():
    logger.info("Processing Automated Observations")
    client = CareClient()
    monitors = client.get("/api/vitals_observation_device/automated_observations/")
    logger.info(f"Found {len(monitors)} monitors")
    for monitor in monitors:
        logger.info(
            f"Processing Monitor w. endpoint address: {monitor["endpoint_address"]}"
        )
        data = get_static_observations(device_id=monitor["endpoint_address"])
        if not data:
            logger.info(
                f"No data found for vitals observation device ({monitor['endpoint_address']})"
            )
            continue
        observations = get_entries_for_automated_observations(data)
        client.post(
            f"/api/vitals_observation_device/automated_observations/{monitor["id"]}/record/",
            data=[observation.model_dump(mode="json") for observation in observations],
        )
        logger.info(f"Processed {len(observations)} observations")
