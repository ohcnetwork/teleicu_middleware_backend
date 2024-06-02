from django.urls import path, re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r"mock_req/$", consumers.mock_request_consumer.as_asgi()),
    path(
        r"observations/<str:ip_address>",
        consumers.observations.as_asgi(),
    ),
]
