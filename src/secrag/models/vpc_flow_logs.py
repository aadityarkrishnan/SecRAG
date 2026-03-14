from sqlalchemy import Column, String, Integer, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from secrag.models.base import Base


class VPCFlowLog(Base):
    __tablename__ = "vpc_flow_logs"

    __table_args__ = (
        UniqueConstraint(
            "src_addr",
            "dst_addr",
            "src_port",
            "dst_port",
            "start_time",
            name="uq_vpc_flow_unique"
        ),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    src_addr = Column(String, index=True)
    dst_addr = Column(String, index=True)

    src_port = Column(Integer)
    dst_port = Column(Integer)

    protocol = Column(Integer)

    packets = Column(Integer)
    bytes = Column(Integer)

    start_time = Column(DateTime(timezone=True))
    end_time = Column(DateTime(timezone=True))

    action = Column(String)
    log_status = Column(String)

    inserted_at = Column(DateTime(timezone=True), server_default=func.now())