from django.conf import settings
import requests
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from middleware.utils import generate_jwt


@api_view(["GET"])
def test_route(request):
    return Response({"result": "healthy"}, status=status.HTTP_200_OK)


@api_view(["POST"])
def get_mock_request_list(request):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "send_mock_req", {"type": "send_mock_req", "message": request.data}
    )
    return Response({"result": "Received request"}, status=status.HTTP_200_OK)


@api_view(["POST"])
def verify_token(request):
    print(request.data)
    token = request.data["token"]

    if not token:
        return Response(
            {"error": "no token provided"}, status=status.HTTP_401_UNAUTHORIZED
        )
    res = requests.post(settings.CARE_VERIFY_TOKEN_URL, data={"token": token})
    res.raise_for_status()
    middleware_token = generate_jwt(exp=60 * 20)
    return Response({"token": {middleware_token}}, status=status.HTTP_200_OK)
