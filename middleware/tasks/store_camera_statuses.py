import logging
from typing import Dict

from celery import shared_task
from django.conf import settings

from middleware.camera.onvif_zeep_camera_controller import OnvifZeepCameraController
from middleware.camera.types import CameraAsset
from middleware.models import Asset, AssetClasses
from middleware.observation.types import DeviceID
from middleware.redis_manager import redis_manager

logger = logging.getLogger(__name__)


@shared_task
def store_camera_statuses():
    cameras = Asset.objects.filter(type=AssetClasses.ONVIF.name, deleted=False)
    device_data: Dict[DeviceID, str] = {}
    for camera in cameras:
        cam_request = CameraAsset(
            hostname=str(camera.ip_address),
            port=int(camera.port),
            username=str(camera.username),
            password=str(camera.password),
        )
        cam = OnvifZeepCameraController(req=cam_request)
        response = cam.get_status()
        if response and response.get("error") == "NO error":
            device_data[camera.ip_address] = "up"
        else:
            device_data[camera.ip_address] = "down"

    redis_manager.push_to_redis(settings.CAMERA_STATUS_KEY, device_data)
