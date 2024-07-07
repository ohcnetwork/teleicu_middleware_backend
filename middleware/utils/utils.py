from typing import Dict, List
from uuid import UUID
import requests
from django.conf import settings

from middleware.token_generator import generate_jwt
from typing import List, Dict, TypeVar, Any
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

def _get_headers(claims: dict = None) -> dict:
    return {
        "Authorization": "Middleware_Bearer " + generate_jwt(claims=claims),
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


def group_by(data: List[T], key: str) -> Dict[Any, List[T]]:
    grouped_data: Dict[Any, List[T]] = {}
    for item in data:
        group_key = getattr(item, key)
        if group_key in grouped_data:
            grouped_data[group_key].append(item)
        else:
            grouped_data[group_key] = [item]
    return grouped_data


def get_patient_id(external_id: UUID):

    response = requests.get(
        f"{settings.CARE_URL}consultation/patient_from_asset/?preset_name=monitor",
        headers=_get_headers(claims={"asset_id": str(external_id)}),
    )
    response.raise_for_status()
    data = response.json()
    print("data is ", data)
    return (
        data.get("consultation_id"),
        data.get("patient_id"),
        data.get("bed_id"),
        data.get("asset_beds"),
    )
