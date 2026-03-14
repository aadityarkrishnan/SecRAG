from datetime import datetime
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uuid


class CloudTrailBase(BaseModel):
    event_id: Optional[str]
    event_time: Optional[datetime]
    event_source: Optional[str]
    event_name: Optional[str]

    aws_region: Optional[str]
    source_ip: Optional[str]
    user_name: Optional[str]

    read_only: Optional[bool]

    raw_event: Optional[Dict[str, Any]]


class CloudTrailCreate(CloudTrailBase):
    pass


class CloudTrailResponse(CloudTrailBase):
    id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True