import json
import logging

import requests
from django.conf import settings
from django.http import HttpResponse
from rest_framework import status
from rest_framework.exceptions import APIException

from middleware.utils import generate_jwt

logger = logging.getLogger(__name__)


class CareClient:
    auth_header_type = "Gateway_Bearer"

    def __init__(self):
        self.base_url = settings.CARE_API
        self.timeout = settings.CARE_API_TIMEOUT

    def _get_url(self, endpoint):
        return f"{self.base_url}{endpoint}"

    def _get_headers(self):
        return {
            "Authorization": f"{self.auth_header_type} {generate_jwt()}",
            "X-Gateway-Id": settings.GATEWAY_DEVICE_ID,
            "Accept": "application/json",
        }

    def _make_request(
        self, method: str, url: str, as_http_response=False, **request_kwargs
    ) -> HttpResponse | dict:
        """
        Execute the HTTP request and validate the response.

        Args:
            method: HTTP method (GET, POST, etc.)
            url: Full URL to request
            as_http_response: If True, return HttpResponse object instead of JSON
            **request_kwargs: Additional arguments to pass to requests method

        Returns:
            HttpResponse or dict depending on as_http_response flag

        Raises:
            APIException: For all request failures with appropriate error messages
        """
        try:
            response = requests.request(
                method, url, timeout=self.timeout, **request_kwargs
            )

            # Handle response based on format requested
            if as_http_response:
                return HttpResponse(
                    response.content,
                    content_type=response.headers.get(
                        "content-type", "application/json"
                    ),
                    status=response.status_code,
                )

            if response.status_code >= status.HTTP_400_BAD_REQUEST:
                raise APIException(response.text, response.status_code)

            return response.json()

        except requests.Timeout as e:
            raise APIException(
                {"error": f"Request timed out after {self.timeout} seconds"},
                status.HTTP_504_GATEWAY_TIMEOUT,
            ) from e
        except (
            requests.ConnectionError,
            requests.exceptions.SSLError,
            requests.exceptions.TooManyRedirects,
            requests.RequestException,
        ) as e:
            logger.error(f"Gateway connection error: {str(e)}")
            raise APIException(
                {"error": "Failed to connect to gateway device"},
                status.HTTP_503_SERVICE_UNAVAILABLE,
            ) from e
        except json.decoder.JSONDecodeError as e:
            raise APIException(
                {"error": "Invalid JSON response from gateway device"},
                status.HTTP_502_BAD_GATEWAY,
            ) from e
        except Exception as e:
            logger.error(f"Unexpected error during gateway request: {str(e)}")
            raise APIException(
                {"error": "An unexpected error occurred during gateway request"},
                status.HTTP_500_INTERNAL_SERVER_ERROR,
            ) from e

    def get(self, endpoint, data=None, as_http_response=False):
        url = self._get_url(endpoint)
        return self._make_request(
            "GET",
            url,
            as_http_response=as_http_response,
            params=data,
            headers=self._get_headers(),
        )

    def post(self, endpoint, data=None, as_http_response=False):
        url = self._get_url(endpoint)
        return self._make_request(
            "POST",
            url,
            as_http_response=as_http_response,
            json=data,
            headers=self._get_headers(),
        )
