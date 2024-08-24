import logging
from django.apps import AppConfig
logger = logging.getLogger(__name__)
from django.core.cache import cache

class MiddlewareConfig(AppConfig):
    name = "middleware"
    verbose_name = "Middleware"

    def ready(self):
        cache.clear()
