from typing import Dict, Optional

from ..utils import group_by
from ..serializers.observation import (
    ObservationIDChoices,
    ObservationSerializer,
)


class ObservationsMap:
    _observations = {}

    def get(self, id):
        return self._observations[id]

    def set(self, data):
        if data:
            new_data = group_by(data, "device_id")
            for key, data in new_data.items():
                if data:
                    self._observations[key] = data
