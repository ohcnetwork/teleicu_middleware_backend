from django.urls import path, re_path
from . import consumers

websocket_urlpatterns = [
    path(r"logger", consumers.LoggerConsumer.as_asgi()),
    path(
        r"observations/<str:ip_address>",
        consumers.observations.as_asgi(),
    ),
]
