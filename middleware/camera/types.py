from typing import Dict, Optional
from pydantic import AliasChoices, BaseModel, Field

from middleware.observation.types import DeviceID


class CameraAsset(BaseModel):
    hostname: str
    username: str
    password: str
    port: int
    useSecure: Optional[bool]=None

class CameraAssetPresetRequest(CameraAsset):
    preset: int = Field(
        default=None, validation_alias=AliasChoices("preset", "presetName")
    )

class CameraAssetMoveRequest(CameraAsset):
    x: float
    y: float
    zoom: float


class CameraStatus:
    time: str
    status: Dict[DeviceID, str]
