from rest_framework.exceptions import APIException
from rest_framework import status


class InvalidCameraCrendentialsException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Invalid Credentials"
    default_code = "camera_error"
