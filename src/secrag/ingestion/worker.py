import asyncio
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from secrag.core.database import AsyncSessionLocal
from secrag.ingestion.cloudtrail_ingest import ingest_cloudtrail_file
from secrag.ingestion.guardduty_ingest import ingest_guardduty_file
from secrag.ingestion.vpc_flow_ingest import ingest_vpc_flow_file

logger = logging.getLogger(__name__)


async def run_ingestion():

    logger.info("Starting ingestion worker")

    while True:

        try:
            async with AsyncSessionLocal() as db:

                cloudtrail_count = await ingest_cloudtrail_file(
                    "docs/cloudtrail_logs.json", db
                )

                guardduty_count = await ingest_guardduty_file(
                    "docs/guardduty_findings.json", db
                )

                vpcflow_count = await ingest_vpc_flow_file(
                    "docs/vpc_flow_logs.log", db
                )

                logger.info(
                    f"Ingestion complete: "
                    f"CloudTrail={cloudtrail_count}, "
                    f"GuardDuty={guardduty_count}, "
                    f"VPCFlow={vpcflow_count}"
                )

        except Exception as e:
            logger.error(f"Ingestion error: {e}")

        # run every 60 seconds
        await asyncio.sleep(60)