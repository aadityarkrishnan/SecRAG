from datetime import datetime
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uuid


class GuardDutyBase(BaseModel):
    finding_id: Optional[str]
    finding_type: Optional[str]

    severity: Optional[float]

    region: Optional[str]
    resource_type: Optional[str]

    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    raw_finding: Optional[Dict[str, Any]]


class GuardDutyCreate(GuardDutyBase):
    pass


class GuardDutyResponse(GuardDutyBase):
    id: uuid.UUID
    inserted_at: datetime

    class Config:
        from_attributes = True