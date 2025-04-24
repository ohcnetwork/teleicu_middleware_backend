from django.urls import include, path
from rest_framework.routers import SimpleRouter

from middleware.stream.views import MiddlewareStreamViewSet

router = SimpleRouter(trailing_slash=False)
router.register(r"", MiddlewareStreamViewSet, basename="stream")

urlpatterns = [
    path("", include(router.urls)),
]
