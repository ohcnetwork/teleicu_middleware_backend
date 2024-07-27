import logging
from django.apps import AppConfig
logger = logging.getLogger(__name__)

class MiddlewareConfig(AppConfig):
    name = "middleware"
    verbose_name = "Middleware"

    def ready(self):
        from middleware.tasks import retrieve_asset_config

        # countdown to get the middleware running for authentication
        retrieve_asset_config.apply_async(countdown=2)
