from datetime import datetime
from django.core.cache import cache

import json
from typing import Dict, List

from django.conf import settings
from middleware.redis_manager import redis_manager
from middleware.observation.utils import update_stored_observations
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.response import Response
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


from middleware.utils import group_by

from middleware.observation.types import DeviceID, Status


from middleware.observation.types import (
    Observation,
    ObservationID,
    ObservationList,
)

from middleware.authentication import CareAuthentication

@api_view(["GET"])
@authentication_classes([CareAuthentication])
def sample_authentication(request):
    return Response({"result": "Authenticated"}, status=status.HTTP_200_OK)


@api_view(["GET"])
def device_statuses(request):
    statuses = redis_manager.get_queue_items("monitor_statuses")

    return Response(statuses, status=status.HTTP_200_OK)


@api_view(["POST"])
def update_observations(request):
    data = flatten_observations(request.data)
    store_and_send_observations(data)

    return Response({"result": "Successful"}, status=status.HTTP_200_OK)


# As we dont get the blood pressure data every single time
# in order to get continuous data we take the previous data
# to store previous value of blood pressure per device_id
def update_blood_pressure(observations: List[Observation]):
    for observation in observations:
        if observation.observation_id == ObservationID.BLOOD_PRESSURE:
            cache.set(f"blood_pressure_{observation.device_id}", observation)


def flatten_observations(observations):
    if isinstance(observations, list):
        flattened_list = []
        for observation in observations:
            flattened_list.extend(flatten_observations(observation))
        return flattened_list
    else:
        return [observations]


def store_and_send_observations(data: List):
    observation_data: List[Observation] = ObservationList.model_validate(data).root

    # TODO
    # addStatusData

    # store observations in redis
    update_stored_observations(observation_data)

    # store last blood pressure value for devices
    update_blood_pressure(observation_data)

    channel_layer = get_channel_layer()
    grouped_observations = group_by(data=observation_data, key="device_id")
    device_data: Dict[DeviceID, str] = {}
    for device_id, observation_list in grouped_observations.items():
        if observation_list[0].status == Status.DISCONNECTED:
            device_data[device_id] = "down"
        else:
            device_data[device_id] = "up"
        last_blood_pressure_data = cache.get(f"blood_pressure_{device_id}")
        if last_blood_pressure_data:
            observation_list.append(last_blood_pressure_data)
        async_to_sync(channel_layer.group_send)(
            f"ip_{device_id}",
            {
                "type": "send_observation",
                "message": [
                    observation.model_dump(mode="json", by_alias=True)
                    for observation in observation_list
                ],
            },
        )
    redis_manager.push_to_queue("monitor_statuses", device_data)
