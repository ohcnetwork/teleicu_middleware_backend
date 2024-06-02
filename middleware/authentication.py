from rest_framework import HTTP_HEADER_ENCODING
import logging
from django.core.cache import cache
import requests

from rest_framework_simplejwt.authentication import JWTAuthentication
import jwt
from rest_framework_simplejwt.exceptions import AuthenticationFailed, InvalidToken
from django.core.exceptions import ValidationError

from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import Token

logger = logging.getLogger(__name__)


def jwk_response_cache_key(url: str) -> str:
    return f"jwk_response:{url}"


class MiddlewareUser(AnonymousUser):
    """
    Read-only user class for middleware authentication
    """

    def __init__(self, facility, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.facility = facility
        # self.username = f"middleware{facility.external_id}"
        self.username = f"middleware_123"

    @property
    def is_authenticated(self):
        return True

class MiddlewareAuthentication(JWTAuthentication):
    """
    An authentication plugin that authenticates requests through a JSON web
    token provided in a request header.
    """

    facility_header = "X-Facility-Id"
    auth_header_type = "Care_Bearer"
    auth_header_type_bytes = auth_header_type.encode(HTTP_HEADER_ENCODING)

    def get_public_key(self, url):
        public_key_json = cache.get(jwk_response_cache_key(url))
        if not public_key_json:
            res = requests.get(url)
            res.raise_for_status()
            public_key_json = res.json()
            cache.set(jwk_response_cache_key(url), public_key_json, timeout=60 * 5)
        return public_key_json["keys"][0]

    def open_id_authenticate(self, url, token):
        public_key_response = self.get_public_key(url)
        public_key = jwt.algorithms.RSAAlgorithm.from_jwk(public_key_response)
        print(public_key)
        print(jwt.decode(token, key=public_key, algorithms=["RS256"]))
        return jwt.decode(token, key=public_key, algorithms=["RS256"])

    def authenticate_header(self, request):
        return f'{self.auth_header_type} realm="{self.www_authenticate_realm}"'

    def get_user(self, _: Token, facility: int):
        return MiddlewareUser(facility=facility)

    def authenticate(self, request):
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)

        # if raw_token is None or self.facility_header not in request.headers:
        #     return None

        if raw_token is None:
            return None

        # external_id = request.headers[self.facility_header]

        # try:
        #     facility = Facility.objects.get(external_id=external_id)
        # except (Facility.DoesNotExist, ValidationError) as e:
        #     raise InvalidToken({"detail": "Invalid Facility", "messages": []}) from e

        # if not facility.middleware_address:
        #     raise InvalidToken({"detail": "Facility not connected to a middleware"})

        open_id_url = f"http://127.0.0.1:9000/.well-known/openid-configuration"
        validated_token = self.get_validated_token(open_id_url, raw_token)

        # return self.get_user(validated_token, facility), validated_token
        return self.get_user(validated_token, 123), validated_token

    def get_raw_token(self, header):
        """
        Extracts an un-validated JSON web token from the given "Authorization"
        header value.
        """
        parts = header.split()

        if len(parts) == 0:
            # Empty AUTHORIZATION header sent
            return None

        if parts[0] != self.auth_header_type_bytes:
            # Assume the header does not contain a JSON web token

            return None

        if len(parts) != 2:
            raise AuthenticationFailed(
                ("Authorization header must contain two space-delimited values"),
                code="bad_authorization_header",
            )
        return parts[1]

    def get_validated_token(self, url, raw_token):
        """
        Validates an encoded JSON web token and returns a validated token
        wrapper object.
        """

        try:
            return self.open_id_authenticate(url, raw_token)
        except Exception as e:
            logger.info(e, "Token: ", raw_token)

        raise InvalidToken({"detail": "Given token not valid for any token type"})
