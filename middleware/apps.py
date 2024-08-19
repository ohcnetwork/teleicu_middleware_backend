import logging
from django.apps import AppConfig
logger = logging.getLogger(__name__)
from django.core.cache import cache

class MiddlewareConfig(AppConfig):
    name = "middleware"
    verbose_name = "Middleware"

    def ready(self):
        from middleware.tasks import retrieve_asset_config, store_camera_statuses

        # countdown to get the middleware running for authentication

        retrieve_asset_config.apply_async(countdown=2)
        store_camera_statuses.apply_async()
