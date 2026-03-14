import strawberry
from datetime import datetime
from uuid import UUID


@strawberry.type
class GuardDutyFindingType:
    id: UUID
    finding_id: str | None
    finding_type: str | None
    severity: float | None
    region: str | None
    resource_type: str | None
    created_at: datetime | None
    updated_at: datetime | None


@strawberry.type
class CloudTrailEventType:
    id: UUID
    event_id: str | None
    event_name: str | None
    event_source: str | None
    aws_region: str | None
    user_name: str | None
    source_ip: str | None
    event_time: datetime | None


@strawberry.type
class VPCFlowLogType:
    id: UUID
    src_addr: str | None
    dst_addr: str | None
    src_port: int | None
    dst_port: int | None
    protocol: int | None
    action: str | None
    start_time: datetime | None