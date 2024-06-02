from uuid import UUID
from celery import shared_task
import requests
from django.conf import settings

from middleware.models import Asset
from middleware.utils import _get_headers


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
