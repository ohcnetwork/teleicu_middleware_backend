import logging
from django.apps import AppConfig
logger = logging.getLogger(__name__)

class MiddlewareConfig(AppConfig):
    name = "middleware"
    verbose_name = "Middleware"

    def ready(self):
        # from middleware.tasks import retrieve_asset_config

        # retrieve_asset_config()
        logger.info("startup function called")
