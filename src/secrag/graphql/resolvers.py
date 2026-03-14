import strawberry
from strawberry.types import Info
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from secrag.models.guardduty import GuardDutyFinding
from secrag.models.cloudtrail import CloudTrailEvent
from secrag.models.vpc_flow_logs import VPCFlowLog

from .types import (
    GuardDutyFindingType,
    CloudTrailEventType,
    VPCFlowLogType
)


@strawberry.type
class Query:

    @strawberry.field
    async def guardduty_findings(self, info: Info) -> list[GuardDutyFindingType]:

        db: AsyncSession = info.context["db"]

        result = await db.execute(select(GuardDutyFinding))

        return result.scalars().all()


    @strawberry.field
    async def cloudtrail_events(self, info: Info) -> list[CloudTrailEventType]:

        db: AsyncSession = info.context["db"]

        result = await db.execute(select(CloudTrailEvent))

        return result.scalars().all()


    @strawberry.field
    async def vpc_flow_logs(self, info: Info) -> list[VPCFlowLogType]:

        db: AsyncSession = info.context["db"]

        result = await db.execute(select(VPCFlowLog))

        return result.scalars().all()