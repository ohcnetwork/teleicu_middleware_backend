from rest_framework.exceptions import APIException
from rest_framework import status


class InvalidCameraCredentialsException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Invalid Credentials"
    default_code = "camera_error"


class CameraLockedException(APIException):
    status_code = status.HTTP_423_LOCKED
    default_detail = "Camera is Locked"
    default_code = "camera_error"
