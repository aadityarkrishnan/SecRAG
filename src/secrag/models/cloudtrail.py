from sqlalchemy import Column, String, DateTime, Boolean, JSON, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from secrag.models.base import Base


class CloudTrailEvent(Base):
    __tablename__ = "cloudtrail_events"

    __table_args__ = (
        UniqueConstraint("event_id", name="uq_cloudtrail_event_id"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    event_id = Column(String, index=True)
    event_time = Column(DateTime(timezone=True), index=True)
    event_source = Column(String)
    event_name = Column(String)

    aws_region = Column(String)
    source_ip = Column(String)
    user_name = Column(String)

    read_only = Column(Boolean)

    raw_event = Column(JSON)

    created_at = Column(DateTime(timezone=True), server_default=func.now())