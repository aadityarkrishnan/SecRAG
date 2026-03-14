from secrag.core.database import engine
from secrag.models.base import Base

from secrag.models import cloudtrail
from secrag.models import guardduty
from secrag.models import vpc_flow_logs


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)