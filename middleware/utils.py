from typing import Dict, List
from .token_generator import generate_jwt
from django.conf import settings


def _get_headers() -> dict:
    return {
        "Authorization": "Middleware_Bearer " + generate_jwt(),
        "Content-Type": "application/json",
        "X-Facility-Id": settings.FACILITYID,
    }


def group_by(data, key):
    grouped_data: Dict[str, List] = {}
    for item in data:
        group_key = item[key]
        if group_key in grouped_data:
            grouped_data[group_key].append(item)
        else:
            grouped_data[group_key] = [item]
    return grouped_data
