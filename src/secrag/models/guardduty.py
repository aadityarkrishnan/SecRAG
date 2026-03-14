from sqlalchemy import Column, String, Float, DateTime, JSON, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from secrag.models.base import Base


class GuardDutyFinding(Base):
    __tablename__ = "guardduty_findings"
    __table_args__ = (
        UniqueConstraint("finding_id", name="uq_guardduty_finding_id"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    finding_id = Column(String, index=True)
    finding_type = Column(String, index=True)

    severity = Column(Float, index=True)

    region = Column(String, index=True)

    resource_type = Column(String, index=True)

    created_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True))

    raw_finding = Column(JSON)

    inserted_at = Column(DateTime(timezone=True), server_default=func.now())