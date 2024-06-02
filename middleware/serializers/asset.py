from rest_framework.serializers import (
    CharField,
    ModelSerializer,
    UUIDField,
)

from rest_framework import serializers

from middleware.models import Asset


class AssetConfigSerializer(ModelSerializer):
    id = UUIDField(source="external_id", read_only=True)
    type = CharField()
    description = CharField(default="")
    ip_address = CharField(default="")
    access_key = CharField(default="")
    username = CharField(default="")
    password = CharField(default="")
    port = serializers.IntegerField(default=80)

    class Meta:
        model = Asset
