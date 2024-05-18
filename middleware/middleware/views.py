import requests
from rest_framework import status
from rest_framework.decorators import api_view,authentication_classes
from rest_framework.response import Response
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.conf import settings

from .authentication import MiddlewareAuthentication


from .token_generator import generate_jwt


def _get_headers() -> dict:
    return {
        "Authorization": "Middleware_Bearer " + generate_jwt(),
        "Content-Type": "application/json",
        "X-Facility-Id": settings.FACILITYID,
    }


@api_view(['POST'])
def get_mock_request_list(request):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "send_mock_req", {"type": "send_mock_req", "message": request.data}
    )
    return Response({"result": "Received request"}, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([MiddlewareAuthentication])
def sample_authentication(request):
    return Response({"result": "Authenticated"}, status=status.HTTP_200_OK)


@api_view(['GET'])
def retrieve_asset_config(request):

    response = requests.get(
        f"{settings.CARE_URL}asset_config/?middleware_hostname={settings.HOST_NAME}",
        headers=_get_headers(),
    )

    response.raise_for_status()

    response=response.json()

    
    return Response({"result": response}, status=status.HTTP_200_OK)


@api_view(["GET"])
def test_route(request):
    return Response({"result": "healthy"}, status=status.HTTP_200_OK)
