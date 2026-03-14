from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert

from secrag.models.vpc_flow_logs import VPCFlowLog

BATCH_SIZE = 200


def parse_vpc_line(line: str):

    parts = line.strip().split()

    if len(parts) < 14:
        return None

    return {
        "src_addr": parts[3],
        "dst_addr": parts[4],
        "src_port": int(parts[5]),
        "dst_port": int(parts[6]),
        "protocol": int(parts[7]),
        "packets": int(parts[8]),
        "bytes": int(parts[9]),
        "start_time": datetime.utcfromtimestamp(int(parts[10])),
        "end_time": datetime.utcfromtimestamp(int(parts[11])),
        "action": parts[12],
        "log_status": parts[13],
    }


async def ingest_vpc_flow_file(file_path: str, db: AsyncSession):

    rows = []

    with open(file_path, "r") as f:
        for line in f:

            if line.startswith("version"):
                continue

            parsed = parse_vpc_line(line)

            if parsed:
                rows.append(parsed)

    total_inserted = 0

    for i in range(0, len(rows), BATCH_SIZE):

        batch = rows[i:i+BATCH_SIZE]

        stmt = insert(VPCFlowLog).values(batch)

        stmt = stmt.on_conflict_do_nothing(
            constraint="uq_vpc_flow_unique"
        )

        result = await db.execute(stmt)

        total_inserted += result.rowcount

    await db.commit()

    return total_inserted