from datetime import datetime
from pydantic import BaseModel
from typing import Optional
import uuid


class VPCFlowBase(BaseModel):
    src_addr: Optional[str]
    dst_addr: Optional[str]

    src_port: Optional[int]
    dst_port: Optional[int]

    protocol: Optional[int]

    packets: Optional[int]
    bytes: Optional[int]

    start_time: Optional[datetime]
    end_time: Optional[datetime]

    action: Optional[str]
    log_status: Optional[str]


class VPCFlowCreate(VPCFlowBase):
    pass


class VPCFlowResponse(VPCFlowBase):
    id: uuid.UUID
    inserted_at: datetime

    class Config:
        from_attributes = True