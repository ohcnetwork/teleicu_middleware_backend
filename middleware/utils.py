import logging
from datetime import datetime
from typing import Any, Dict, List, TypeVar

import pytz
from authlib.jose import jwt
from django.conf import settings
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)
logger = logging.getLogger(__name__)


def generate_jwt(claims=None, exp=60, jwks=None):
    if claims is None:
        claims = {}
    if jwks is None:
        jwks = settings.JWKS
    header = {"alg": "RS256"}
    time = int(datetime.now().timestamp())
    payload = {
        "iat": time,
        "exp": time + exp,
        **claims,
    }
    return jwt.encode(header, payload, jwks).decode("utf-8")


def _get_headers(claims: dict = None) -> dict:
    return {
        "Authorization": "Gateway_Bearer " + generate_jwt(claims=claims),
        "Content-Type": "application/json",
        "X-Gateway-Id": settings.GATEWAY_DEVICE_ID,
    }


def group_by(data: List[T], key: str) -> Dict[Any, List[T]]:
    grouped_data: Dict[Any, List[T]] = {}
    for item in data:
        group_key = getattr(item, key)
        if group_key in grouped_data:
            grouped_data[group_key].append(item)
        else:
            grouped_data[group_key] = [item]
    return grouped_data


def get_current_truncated_utc_z():
    current_time = datetime.now(pytz.UTC)
    truncated_time = current_time.replace(second=0, microsecond=0)
    return truncated_time.strftime("%Y-%m-%dT%H:%M:00.000Z")
