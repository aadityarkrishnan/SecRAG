# SecRAG Project Progress – Part 2

## Overview

This document records the progress made after the initial setup of the SecRAG project.
It covers the following additions:

* Log ingestion for GuardDuty and VPC Flow Logs
* Data parsing improvements
* GraphQL API integration
* Issues encountered and their resolutions

---

# 1. GuardDuty Log Ingestion

## Objective

Create an ingestion pipeline that reads GuardDuty findings from a JSON file and stores them in PostgreSQL.

## Implementation

Created module:

```
src/secrag/ingestion/guardduty_ingest.py
```

Main steps:

1. Read GuardDuty JSON file
2. Parse relevant fields
3. Map to SQLAlchemy model
4. Insert records into PostgreSQL

Example ingestion flow:

```
GuardDuty JSON
      ↓
Parser
      ↓
Pydantic Schema
      ↓
SQLAlchemy Model
      ↓
PostgreSQL
```

---

# 2. Issue Encountered – No Records Inserted

## Problem

The ingestion endpoint returned:

```
0 records inserted
```

## Root Cause

GuardDuty JSON structure used capitalized keys:

```
Findings
Id
Type
Severity
Region
CreatedAt
UpdatedAt
Resource
```

But the parser was expecting:

```
findings
id
type
severity
region
createdAt
updatedAt
resource
```

Because of this mismatch, extracted values were `None`.

---

## Resolution

Parser was updated to use the correct field names.

Correct mapping:

| JSON Field            | Parser Field  |
| --------------------- | ------------- |
| Id                    | finding_id    |
| Type                  | finding_type  |
| Severity              | severity      |
| Region                | region        |
| CreatedAt             | created_at    |
| UpdatedAt             | updated_at    |
| Resource.ResourceType | resource_type |

Example fix:

```python
finding_id = finding.get("Id")
finding_type = finding.get("Type")
severity = finding.get("Severity")
region = finding.get("Region")
```

---

# 3. Existing Bad Records Cleanup

Before reinserting correct data, existing rows were cleared.

SQL used:

```
TRUNCATE guardduty_findings;
```

After reinserting logs, all columns populated correctly.

---

# 4. VPC Flow Log Ingestion

## Objective

Parse VPC Flow logs stored as plain text.

Example log format:

```
version account-id interface-id srcaddr dstaddr srcport dstport protocol packets bytes start end action log-status
```

## Implementation

Created module:

```
src/secrag/ingestion/vpc_flow_ingest.py
```

Parsing logic:

1. Read each log line
2. Split fields using whitespace
3. Convert timestamps
4. Insert records into database

Converted timestamps:

```
unix_timestamp → datetime
```

Example conversion:

```python
datetime.utcfromtimestamp(int(parts[10]))
```

---

# 5. GraphQL API Integration

## Objective

Allow querying logs using GraphQL instead of REST.

Advantages:

* Flexible queries
* Select specific fields
* Ideal for investigation workflows

---

# 6. GraphQL Library

Installed:

```
strawberry-graphql
```

Command:

```
uv add strawberry-graphql
```

---

# 7. GraphQL Project Structure

Created new folder:

```
src/secrag/graphql
```

Structure:

```
graphql/
    schema.py
    resolvers.py
    types.py
```

---

# 8. GraphQL Types

GraphQL object types created for:

* GuardDuty findings
* CloudTrail events
* VPC flow logs

Example:

```
GuardDutyFindingType
CloudTrailEventType
VPCFlowLogType
```

These define the fields available in GraphQL queries.

---

# 9. GraphQL Resolvers

Resolvers connect GraphQL queries to the database.

Example resolver:

```
guardduty_findings
cloudtrail_events
vpc_flow_logs
```

Each resolver:

1. Gets database session from context
2. Executes SQLAlchemy query
3. Returns results

Example query execution:

```
SELECT * FROM guardduty_findings
```

---

# 10. Issue Encountered – Strawberry GraphQL Error

## Error

```
MissingArgumentsAnnotationsError:
Missing annotation for argument "info"
```

## Cause

Strawberry requires resolver arguments to be type annotated.

The resolver was written as:

```
async def guardduty_findings(self, info)
```

Without specifying the type.

---

## Resolution

Added type annotation using Strawberry `Info`.

Import added:

```
from strawberry.types import Info
```

Correct resolver signature:

```
async def guardduty_findings(self, info: Info)
```

This allowed Strawberry to correctly build the GraphQL schema.

---

# 11. GraphQL Router Setup

GraphQL endpoint added to FastAPI.

Endpoint path:

```
/graphql
```

Integrated using Strawberry GraphQL router.

---

# 12. Testing GraphQL

Server started using:

```
uv run uvicorn secrag.main:app --reload
```

GraphQL playground opened at:

```
http://localhost:8000/graphql
```

---

# 13. Example Queries

### GuardDuty Query

```
query {
  guarddutyFindings {
    findingId
    findingType
    severity
    region
  }
}
```

---

### CloudTrail Query

```
query {
  cloudtrailEvents {
    eventName
    eventSource
    userName
    sourceIp
    eventTime
  }
}
```

---

### VPC Flow Logs Query

```
query {
  vpcFlowLogs {
    srcAddr
    dstAddr
    srcPort
    dstPort
    action
  }
}
```

---

# 14. Current Architecture

Current system architecture:

```
AWS Logs
   ↓
FastAPI Ingestion
   ↓
PostgreSQL
   ↓
GraphQL API
   ↓
Future RAG Analysis
```

---

# 15. Next Planned Steps

Upcoming work for SecRAG:

### 1. GraphQL Filtering

Allow queries such as:

```
severity > 8
eventName = DeleteBucket
src_ip = X
```

### 2. Unified Security Event Model

Create normalized event table combining:

```
CloudTrail
GuardDuty
VPC Flow Logs
```

### 3. Vector Embeddings

Convert security events into embeddings for RAG.

### 4. AI Investigation Queries

Example queries:

```
Which IP triggered GuardDuty before an IAM privilege escalation?
```

```
What suspicious activity occurred before a resource deletion?
```

---

# Status Summary

| Component              | Status    |
| ---------------------- | --------- |
| FastAPI Project        | Completed |
| PostgreSQL Integration | Completed |
| Alembic Migration      | Completed |
| CloudTrail Ingestion   | Completed |
| GuardDuty Ingestion    | Completed |
| VPC Flow Log Ingestion | Completed |
| GraphQL API            | Completed |
| GraphQL Playground     | Working   |

---

# End of Document
