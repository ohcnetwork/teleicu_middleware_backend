from pydantic import BaseModel
from datetime import datetime
from pydantic import UUID4


class LabAnalyzerAsset(BaseModel):
    hostname: str
    port: int

class LabAnalyzerOrder(LabAnalyzerAsset):
    payload: dict


class LabAnalyzerResultModel(BaseModel):
    asset_external_id: UUID4
    ip_address: str
    test_id: str
    status: str
    data: str
    time: datetime
