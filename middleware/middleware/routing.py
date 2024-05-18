from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r"mock_req/$", consumers.mock_request_consumer.as_asgi()),
]
