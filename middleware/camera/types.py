




from typing import Optional
from pydantic import AliasChoices, BaseModel, Field


class CameraAsset(BaseModel):
    hostname: str
    username: str
    password: str
    port: int
    useSecure: Optional[bool]=None

class CameraAssetPresetRequest(CameraAsset):
    preset_name:str =Field(default=None, validation_alias=AliasChoices('preset', 'presetName'))

class CameraAssetMoveRequest(CameraAsset):
    x:float
    y:float
    zoom:float