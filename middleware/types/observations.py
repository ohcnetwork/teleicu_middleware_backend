from datetime import datetime
from enum import Enum
from typing import Dict, List, NewType

from pydantic import BaseModel

from middleware.serializers.observation import Observation, ObservationID
from middleware.utils.utils import group_by


DeviceID = NewType("DeviceID", str)


class StaticObservation(BaseModel):
    observations: Dict[ObservationID, List[Observation]]
    last_updated: datetime
