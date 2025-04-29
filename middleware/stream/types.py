from pydantic import BaseModel


class StreamRequestModel(BaseModel):
    ip: str
    _duration: str | None = None


class VideoStreamRequest(StreamRequestModel):
    stream: str


class VitalSteamRequest(StreamRequestModel):
    asset_id: str


class VerifyStreamTokenRequest(BaseModel):
    token: str
    ip: str
    stream: str


class StreamResponse(BaseModel):
    message: str
