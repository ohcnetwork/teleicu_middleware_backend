from django.urls import path,include
from rest_framework.routers import SimpleRouter
from middleware.camera.views import CameraViewSet


router = SimpleRouter(trailing_slash=False)
router.register(r'', CameraViewSet, basename='camera')

urlpatterns = [
    path("", include(router.urls)),
]

