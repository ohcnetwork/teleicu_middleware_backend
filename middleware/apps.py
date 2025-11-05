import logging

from django.apps import AppConfig
from django.core.cache import cache

logger = logging.getLogger(__name__)


class MiddlewareConfig(AppConfig):
    name = "middleware"
    verbose_name = "Middleware"

    def ready(self):
        try:
            cache.clear()
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
