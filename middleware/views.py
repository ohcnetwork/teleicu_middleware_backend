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


from .utils import _get_headers, group_by

from .types.observations import ObservationsMap


from .serializers.observation import ObservationIDChoices, ObservationSerializer
from rest_framework.parsers import JSONParser
from .authentication import MiddlewareAuthentication


from .token_generator import generate_jwt

last_observation_data: Dict[
    ObservationIDChoices, Dict[str, Optional[ObservationSerializer]]
] = {}
latest_observation = ObservationsMap()


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
    data = flatten_observations(request.data)
    serializer = ObservationSerializer(data=data, many=True)

    # channel_layer = get_channel_layer()

    # TODO
    # addLogData
    # addStatusData

    # async_to_sync(channel_layer.group_send)(
    #     "send_mock_req", {"type": "send_mock_req", "message": request.data}
    # )
    # print(data[0])

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
            async_to_sync(channel_layer.group_send)(
                f"ip_{device_id}",
                {
                    "type": "send_observation",
                    "message": observation,
                },
            )
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
            continue

        if observation_id not in last_observation_data:
            last_observation_data[observation_id] = {}

        last_observation_data[observation_id][
            observation.get("device_id")
        ] = observation
