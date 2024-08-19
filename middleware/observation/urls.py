from django.urls import path
from middleware.observation import views

urlpatterns = [
    path("authenticate/", views.sample_authentication),
    path("update_observations", views.update_observations),
    path("devices/status", views.device_statuses),
]
