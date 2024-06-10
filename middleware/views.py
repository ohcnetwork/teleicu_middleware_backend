from datetime import datetime
import json
from typing import Dict, List, Optional
from uuid import UUID
import requests
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.response import Response
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.conf import settings


from .utils.utils import group_by

from .types.observations import DeviceID, LogData, ObservationsMap, StaticObservation


from .serializers.observation import (
    ObservationIDChoices,
    ObservationSerializer,
    StatusChoices,
)

from .authentication import MiddlewareAuthentication

active_devices: List[str] = []

last_observation_data: Dict[
    ObservationIDChoices, Dict[DeviceID, Optional[ObservationSerializer]]
] = {}
latest_observation = ObservationsMap()
log_data: List[LogData] = []
static_observations: List[StaticObservation] = []


@api_view(["POST"])
def get_mock_request_list(request):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "send_mock_req", {"type": "send_mock_req", "message": request.data}
    )
    return Response({"result": "Received request"}, status=status.HTTP_200_OK)


@api_view(["GET"])
@authentication_classes([MiddlewareAuthentication])
def sample_authentication(request):
    return Response({"result": "Authenticated"}, status=status.HTTP_200_OK)


@api_view(["GET"])
def test_route(request):
    return Response({"result": "healthy"}, status=status.HTTP_200_OK)


@api_view(["POST"])
def update_observations(request):
    add_log_data(request.data)
    data = flatten_observations(request.data)
    serializer = ObservationSerializer(data=data, many=True)

    # TODO
    # addLogData
    # addStatusData

    if serializer.is_valid():
        flattened_validated_observations = serializer.data
        update_observation_data(flattened_observations=flattened_validated_observations)
        latest_observation.set(flattened_validated_observations)
        channel_layer = get_channel_layer()
        grouped_observations = group_by(
            data=flattened_validated_observations, key="device_id"
        )
        for device_id, observation in grouped_observations.items():
            last_blood_pressure_data = last_observation_data.get(
                ObservationIDChoices.BLOOD_PRESSURE, None
            )
            if last_blood_pressure_data and last_blood_pressure_data.get(device_id):
                observation.append(last_blood_pressure_data.get(device_id))
            print("sending data", device_id)
            async_to_sync(channel_layer.group_send)(
                f"ip_{device_id}",
                {
                    "type": "send_observation",
                    "message": observation,
                },
            )
        for flattened_validated_observation in flattened_validated_observations:
            add_observation(flattened_validated_observation)

        return Response({"result": "Successful"}, status=status.HTTP_200_OK)
    else:
        print(serializer.errors)
        return Response({"result": serializer.errors}, status=status.HTTP_200_OK)


def flatten_observations(observations):
    if isinstance(observations, list):
        flattened_list = []
        for observation in observations:
            flattened_list.extend(flatten_observations(observation))
        return flattened_list
    else:
        return [observations]


def update_observation_data(
    flattened_observations: List[ObservationSerializer], skip_empty=True
):
    for observation in flattened_observations:
        observation_id: ObservationIDChoices = (
            f'waveform_{observation["wave-name"]}'
            if observation["observation_id"] == "waveform"
            else observation["observation_id"]
        )
        if (
            skip_empty
            and not (observation.get("value") or observation.get("observation.data"))
            and observation.get("status") != "final"
        ):
            return

        if observation_id not in last_observation_data:
            last_observation_data[observation_id] = {}

        last_observation_data[observation_id][
            observation.get("device_id")
        ] = observation


def add_observation(observation: ObservationSerializer):
    if observation.get("device_id") in active_devices:
        for idx, item in enumerate(static_observations):
            if item.device_id == observation.get("device_id"):
                sliced_observations = item.observations.get(
                    observation.get("observation_id"), []
                )[-settings.DEFAULT_LISTING_LIMIT :]
                static_observations[idx] = StaticObservation(
                    device_id=item.device_id,
                    observations={
                        **item.observations,
                        observation.get("observation_id"): sliced_observations
                        + [observation],
                    },
                    last_updated=datetime.now(),
                )

    else:
        active_devices.append(observation.get("device_id"))
        static_observations.append(
            StaticObservation(
                device_id=observation.get("device_id"),
                observations={observation.get("observation_id"): [observation]},
                last_updated=datetime.now(),
            )
        )


def add_log_data(new_data: List[List[ObservationSerializer]]):
    # Slice the log_data to the last DEFAULT_LISTING_LIMIT entries
    global log_data
    if len(log_data) > settings.DEFAULT_LISTING_LIMIT:
        log_data = log_data[-settings.DEFAULT_LISTING_LIMIT :]
    # Create a new LogData entry
    new_log_entry = LogData(date_time=datetime.now(), data=new_data)

    # Append the new entry to the log_data
    log_data.append(new_log_entry)
