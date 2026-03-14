import json
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert

from secrag.models.guardduty import GuardDutyFinding
from secrag.schemas.guardduty import GuardDutyCreate


def parse_guardduty_finding(finding: dict) -> GuardDutyCreate:

    created = None
    if finding.get("CreatedAt"):
        created = datetime.fromisoformat(
            finding["CreatedAt"].replace("Z", "+00:00")
        )

    updated = None
    if finding.get("UpdatedAt"):
        updated = datetime.fromisoformat(
            finding["UpdatedAt"].replace("Z", "+00:00")
        )

    resource_type = None
    if finding.get("Resource"):
        resource_type = finding["Resource"].get("ResourceType")

    return GuardDutyCreate(
        finding_id=finding.get("Id"),
        finding_type=finding.get("Type"),
        severity=finding.get("Severity"),
        region=finding.get("Region"),
        resource_type=resource_type,
        created_at=created,
        updated_at=updated,
        raw_finding=finding
    )


async def ingest_guardduty_file(file_path: str, db: AsyncSession):

    with open(file_path, "r") as f:
        data = json.load(f)

    findings = data.get("Findings") or []

    rows = []

    for finding in findings:

        schema = parse_guardduty_finding(finding)

        rows.append({
            "finding_id": schema.finding_id,
            "finding_type": schema.finding_type,
            "severity": schema.severity,
            "region": schema.region,
            "resource_type": schema.resource_type,
            "created_at": schema.created_at,
            "updated_at": schema.updated_at,
            "raw_finding": schema.raw_finding,
        })

    if not rows:
        return 0

    stmt = insert(GuardDutyFinding).values(rows)

    stmt = stmt.on_conflict_do_nothing(
        index_elements=["finding_id"]
    )

    result = await db.execute(stmt)

    await db.commit()

    return result.rowcount