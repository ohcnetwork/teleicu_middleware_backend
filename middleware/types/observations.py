from datetime import datetime
from typing import Dict, List, NewType
from middleware.serializers.observation import (
    ObservationIDChoices,
    ObservationSerializer,
)
from middleware.utils.utils import group_by


DeviceID = NewType("DeviceID", str)

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


class StaticObservation:
    device_id: str
    observations: Dict[ObservationIDChoices, List[ObservationSerializer]]
    last_updated: datetime

    def __init__(
        self,
        device_id: str,
        observations: Dict[ObservationIDChoices, List[ObservationSerializer]],
        last_updated: datetime,
    ):
        self.device_id = device_id
        self.observations = observations
        self.last_updated = last_updated


class LogData:
    date_time: str
    data = List[List[ObservationSerializer]]

    def __init__(self, date_time: str, data: List[List[ObservationSerializer]]):
        self.date_time = date_time
        self.data = data
