from django.urls import include, path
from rest_framework.routers import SimpleRouter
from middleware.lab_analyzer.views import LabAnalyzerViewSet


router = SimpleRouter(trailing_slash=False)
router.register(r"", LabAnalyzerViewSet, basename="lab-analyzer")

urlpatterns = [
    path("", include(router.urls)),
]
