import json
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert

from secrag.models.cloudtrail import CloudTrailEvent


BATCH_SIZE = 200


def parse_cloudtrail_event(event: dict):

    event_time = None
    if event.get("eventTime"):
        event_time = datetime.fromisoformat(
            event["eventTime"].replace("Z", "+00:00")
        )

    user_name = None
    if event.get("userIdentity"):
        user_name = event["userIdentity"].get("userName")

    return {
        "event_id": event.get("eventID"),
        "event_time": event_time,
        "event_source": event.get("eventSource"),
        "event_name": event.get("eventName"),
        "aws_region": event.get("awsRegion"),
        "source_ip": event.get("sourceIPAddress"),
        "user_name": user_name,
        "read_only": event.get("readOnly"),
        "raw_event": event,
    }


async def ingest_cloudtrail_file(file_path: str, db: AsyncSession):

    with open(file_path, "r") as f:
        data = json.load(f)

    records = data.get("Records", [])

    rows = [parse_cloudtrail_event(event) for event in records]

    total_inserted = 0

    for i in range(0, len(rows), BATCH_SIZE):

        batch = rows[i : i + BATCH_SIZE]

        stmt = insert(CloudTrailEvent).values(batch)

        stmt = stmt.on_conflict_do_nothing(
            index_elements=["event_id"]
        )

        result = await db.execute(stmt)

        total_inserted += result.rowcount

    await db.commit()

    return total_inserted