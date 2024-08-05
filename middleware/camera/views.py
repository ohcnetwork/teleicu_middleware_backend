from pydantic import ValidationError
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from middleware.camera.onvif_zeep_camera_controller import OnvifZeepCameraController
from middleware.camera.types import (
    CameraAsset,
    CameraAssetMoveRequest,
    CameraAssetPresetRequest,
)
import logging

from middleware.camera.utils import is_camera_locked

logger = logging.getLogger(__name__)


class CameraViewSet(viewsets.ViewSet):

    @action(detail=False, methods=["get"])
    def status(self, request):
        cam_request = CameraAsset(
            hostname=str(request.query_params["hostname"]),
            port=int(request.query_params["port"]),
            username=str(request.query_params["username"]),
            password=str(request.query_params["password"]),
        )
        cam = OnvifZeepCameraController(req=cam_request)
        ressponse = cam.get_status()
        return Response(ressponse, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"])
    def presets(self, request):
        try:
            cam_request = CameraAsset(
                hostname=str(request.query_params["hostname"]),
                port=int(request.query_params["port"]),
                username=str(request.query_params["username"]),
                password=str(request.query_params["password"]),
            )
            cam = OnvifZeepCameraController(req=cam_request)
            presets = cam.get_presets()
            return Response(presets, status=status.HTTP_200_OK)

        except Exception as exc:
            logger.error("An exception occurred while getting presets: %s", exc)
            return Response(exc.errors(), status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"], url_name="presets")
    def set_preset(self, request):
        try:
            cam_request = CameraAssetPresetRequest.model_validate(request.data)
            cam = OnvifZeepCameraController(req=cam_request)
            result = cam.set_preset(preset_name=cam_request.preset_name)
            return Response(result, status=status.HTTP_200_OK)

        except Exception as exc:
            logger.error("An exception occurred while getting presets: %s", exc)
            return Response(exc.errors(), status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"], url_name="gotoPreset")
    def go_to_preset(self, request):
        try:
            cam_request = CameraAssetPresetRequest.model_validate(request.data)
        except ValidationError as e:
            return Response(e.errors(), status=status.HTTP_400_BAD_REQUEST)

        if is_camera_locked(cam_request.hostname):
            logger.info("Camera with host: %s is locked.", cam_request.hostname)
            return Response(
                {
                    "message": "Camera is Locked!",
                },
                status=status.HTTP_423_LOCKED,
            )

        cam = OnvifZeepCameraController(req=cam_request)
        response = cam.go_to_preset(preset_name=cam_request.preset_name)
        if not response:
            response = f"Preset {cam_request.preset_name} Not Found"
            return Response(response, status=status.HTTP_404_NOT_FOUND)
        return Response(response, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_name="absoluteMove")
    def absolute_move(self, request):
        try:
            cam_request = CameraAssetMoveRequest.model_validate(request.data)
        except ValidationError as e:
            return Response(e.errors(), status=status.HTTP_400_BAD_REQUEST)

        if is_camera_locked(cam_request.hostname):
            logger.info("Camera with host: %s is locked.", cam_request.hostname)
            return Response(
                {
                    "message": "Camera is Locked!",
                },
                status=status.HTTP_423_LOCKED,
            )

        cam = OnvifZeepCameraController(req=cam_request)
        cam.absolute_move(pan=cam_request.x, tilt=cam_request.y, zoom=cam_request.zoom)
        return Response(
            {"status": "success", "message": "Camera position updated!"},
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["post"], url_name="relativeMove")
    def relative_move(self, request):
        try:
            cam_request = CameraAssetMoveRequest.model_validate(request.data)
        except ValidationError as e:
            return Response(e.errors(), status=status.HTTP_400_BAD_REQUEST)

        if is_camera_locked(cam_request.hostname):
            logger.info("Camera with host: %s is locked.", cam_request.hostname)
            return Response(
                {
                    "message": "Camera is Locked!",
                },
                status=status.HTTP_423_LOCKED,
            )

        cam = OnvifZeepCameraController(req=cam_request)
        cam.relative_move(pan=cam_request.x, tilt=cam_request.y, zoom=cam_request.zoom)
        return Response(
            {"status": "success", "message": "Camera position updated!"},
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["post"], url_name="snapshotAtLocation")
    def snapshot_at_location(self, request):
        try:
            cam_request = CameraAssetMoveRequest.model_validate(request.data)
        except ValidationError as e:
            return Response(e.errors(), status=status.HTTP_400_BAD_REQUEST)

        if is_camera_locked(cam_request.hostname):
            logger.info("Camera with host: %s is locked.", cam_request.hostname)
            return Response(
                {
                    "message": "Camera is Locked!",
                },
                status=status.HTTP_423_LOCKED,
            )
        cam = OnvifZeepCameraController(req=cam_request)
        cam.relative_move(pan=cam_request.x, tilt=cam_request.y, zoom=cam_request.zoom)
        snapshot_uri = cam.get_snapshot_uri()
        return Response(
            {"status": "success", "uri": snapshot_uri},
            status=status.HTTP_200_OK,
        )
