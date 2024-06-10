from typing import Optional
from uuid import UUID
from celery import shared_task
import requests
from django.conf import settings
import logging

from middleware.models import Asset, AssetClasses
from middleware.serializers.observation import DailyRoundObservationSerializer
from middleware.utils.observation_utils import get_vitals_from_observations
from middleware.utils.utils import _get_headers, get_patient_id

logger = logging.getLogger(__name__)

@shared_task
def test_celery_task():
    return print("celery is working ")


@shared_task
def retrieve_asset_config():
    print("retreving assets")
    response = requests.get(
        f"{settings.CARE_URL}asset_config/?middleware_hostname={settings.HOST_NAME}",
        headers=_get_headers(),
    )

    response.raise_for_status()
    data = response.json()
    print("data is", data)
    existing_asset_ids = list(
        Asset.objects.filter(deleted=False).values_list("id", flat=True)
    )
    print("existing", existing_asset_ids)
    missing_asset_ids = [
        asset["id"] for asset in data if UUID(asset["id"]) not in existing_asset_ids
    ]
    print("missing_asset_ids", missing_asset_ids)

    # Mark missing assets as deleted
    deleted_count = Asset.objects.filter(id__in=missing_asset_ids).update(deleted=True)

    print("Deleted assets count:", deleted_count)

    for asset in data:
        # Implement logic to create or update assets based on your model
        new_asset, _ = Asset.objects.update_or_create(
            id=str(asset["id"]), defaults=asset
        )


@shared_task
def automated_daily_rounds():
    print("Automated daily rounds")

    monitors = Asset.objects.filter(type=AssetClasses.HL7MONITOR.name, deleted=False)
    print("Found %s monitors", len(monitors))

    for monitor in monitors:
        print("Processing monitor %s", monitor.id)
        consultation_id, patient_id, bed_id, asset_beds = get_patient_id(
            external_id=monitor.id
        )
        if not consultation_id or not patient_id or not bed_id:
            logger.error("Patient not found for the asset having id: %s", monitor.id)
            return

        vitals: Optional[DailyRoundObservationSerializer] = (
            get_vitals_from_observations(ip_address=monitor.ip_address)
        )
        print("vitals", vitals)
