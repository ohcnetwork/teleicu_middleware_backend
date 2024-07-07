from django.apps import AppConfig


class MiddlewareConfig(AppConfig):
    name = "middleware"
    verbose_name = "Middleware"

    def ready(self):
        # from middleware.tasks import retrieve_asset_config

        # retrieve_asset_config()
        print("startup function called")
