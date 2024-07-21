from django.urls import path,include
from rest_framework.routers import DefaultRouter
from middleware.camera.views import CameraViewSet


router = DefaultRouter()
router.register(r'', CameraViewSet, basename='camera')

urlpatterns = [
     path('', include(router.urls)),
]