from django.db import models
import uuid
from django.utils import timezone
import enum


class AssetClasses(enum.Enum):
    ONVIF = "OnvifAsset"
    HL7MONITOR = "HL7MonitorAsset"
    VENTILATOR = "VentilatorAsset"

ASSET_CLASSES_CHOICES = [(e.value, e.name) for e in AssetClasses]

class Asset(models.Model):
    class AssetType(models.TextChoices):
        HL7MONITOR = "HL7MONITOR", "HL7 Monitor"
        # Add other asset types as needed

    external_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    type = models.CharField(
        max_length=20,
        choices=ASSET_CLASSES_CHOICES,
        default=AssetClasses.HL7MONITOR.value,
    )
    description = models.TextField()
    ip_address = models.GenericIPAddressField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    deleted = models.BooleanField(default=False)
    access_key = models.CharField(max_length=255, null=True, blank=True)
    username = models.CharField(max_length=255, null=True, blank=True)
    password = models.CharField(max_length=255, null=True, blank=True)
    port = models.IntegerField(default=80, null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["external_id", "ip_address"]),
        ]


class DailyRound(models.Model):
    asset_external_id = models.UUIDField()
    status = models.CharField(max_length=255)
    data = models.TextField()
    response = models.TextField()
    time = models.DateTimeField(default=timezone.now)
    asset = models.ForeignKey(
        Asset, on_delete=models.CASCADE, related_name="daily_rounds"
    )

    class Meta:
        indexes = [
            models.Index(fields=["asset_external_id"]),
        ]
