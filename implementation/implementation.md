# SecRAG – Things Done So Far

## Project Overview

**SecRAG** is a FastAPI-based system designed to ingest and analyze cloud security logs (CloudTrail, GuardDuty, VPC Flow Logs) and later power a **RAG-based security analysis engine**.

The system uses:

* **FastAPI** – API layer
* **PostgreSQL** – log storage
* **SQLAlchemy (Async)** – ORM
* **Alembic** – DB migrations
* **Pydantic** – API schemas
* **Docker** – database container
* **uv** – Python package manager

---

# 1. Project Initialization

### Created Project

```bash
mkdir SecRAG
cd SecRAG
uv init
```

### Installed dependencies

```bash
uv add fastapi uvicorn sqlalchemy asyncpg alembic python-dotenv greenlet
```

Key libraries:

| Library       | Purpose                     |
| ------------- | --------------------------- |
| FastAPI       | API framework               |
| SQLAlchemy    | ORM                         |
| asyncpg       | async Postgres driver       |
| psycopg2      | sync driver for Alembic     |
| Alembic       | DB migration                |
| python-dotenv | environment config          |
| greenlet      | SQLAlchemy async dependency |

---

# 2. Project Structure

```
SecRAG
├── alembic
│   └── versions
├── docs
│   ├── cloudtrail_logs.json
│   ├── guardduty_findings.json
│   └── vpc_flow_logs.log
├── src
│   └── secrag
│       ├── api
│       ├── core
│       │   ├── config.py
│       │   └── database.py
│       ├── ingestion
│       ├── models
│       ├── schemas
│       └── main.py
├── pyproject.toml
└── .env
```

---

# 3. FastAPI Application Setup

### Created FastAPI app

```
src/secrag/main.py
```

```python
from fastapi import FastAPI

app = FastAPI(title="SecRAG")

@app.get("/")
async def health():
    return {"status": "SecRAG running"}
```

Run server:

```bash
uv run uvicorn secrag.main:app --reload
```

---

# 4. Issue: FastAPI App Not Found

### Error

```
Attribute "app" not found in module "secrag.main"
```

### Cause

* `app` variable was not properly defined
* Python module path not recognized

### Fix

1. Ensure `__init__.py` exists

```
src/secrag/__init__.py
```

2. Install project package

```bash
uv pip install -e .
```

---

# 5. Environment Configuration

Created `.env`

```
POSTGRES_HOST=localhost
POSTGRES_PORT=5433
POSTGRES_DB=secRAG
POSTGRES_USER=admin
POSTGRES_PASSWORD=admin123
```

### Config loader

```
src/secrag/core/config.py
```

Loads environment variables using `dotenv`.

---

# 6. PostgreSQL Setup

Started Postgres using Docker:

```bash
docker run -d \
--name secRAG-db \
-e POSTGRES_USER=admin \
-e POSTGRES_PASSWORD=admin123 \
-e POSTGRES_DB=secRAG \
-p 5433:5432 \
postgres
```

---

# 7. Async SQLAlchemy Setup

```
src/secrag/core/database.py
```

```python
engine = create_async_engine(DATABASE_URL)

AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)
```

Dependency:

```python
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
```

---

# 8. Issue: Missing Greenlet

### Error

```
ValueError: the greenlet library is required
```

### Cause

SQLAlchemy async internally requires **greenlet**.

### Fix

```bash
uv add greenlet
```

---

# 9. Database Connection Test

Endpoint:

```
GET /db-test
```

Query:

```python
result = await db.execute(text("SELECT 1"))
```

Result:

```json
{"db": 1}
```

Confirmed DB connectivity.

---

# 10. SQLAlchemy Models Created

Models created for:

### CloudTrail

```
cloudtrail_events
```

### GuardDuty

```
guardduty_findings
```

### VPC Flow Logs

```
vpc_flow_logs
```

Schema design:

* Indexed structured fields
* Raw JSON event stored for analysis

Hybrid model used for **SIEM-style storage**.

---

# 11. Pydantic Schemas Added

Directory:

```
src/secrag/schemas
```

Schemas for:

* CloudTrail
* GuardDuty
* VPC Flow Logs

Purpose:

* API validation
* clean response models
* ingestion pipeline transformation

---

# 12. Log Ingestion Pipeline

Implemented ingestion for **CloudTrail JSON**.

Flow:

```
AWS Log
   ↓
Parser
   ↓
Pydantic schema
   ↓
SQLAlchemy model
   ↓
Postgres
```

Endpoint:

```
POST /ingest/cloudtrail
```

Reads:

```
docs/cloudtrail_logs.json
```

---

# 13. Issue: Timezone Error

### Error

```
can't subtract offset-naive and offset-aware datetimes
```

### Cause

Python datetime had timezone (`UTC`) but DB column used:

```
TIMESTAMP WITHOUT TIME ZONE
```

### Fix

Changed model fields to:

```python
DateTime(timezone=True)
```

Which maps to:

```
TIMESTAMP WITH TIME ZONE
```

---

# 14. Database Migrations with Alembic

Initialized Alembic:

```bash
uv run alembic init alembic
```

---

# 15. Issue: Alembic + Async Engine

### Error

```
MissingGreenlet
```

### Cause

Alembic cannot use async driver.

### Fix

Use separate drivers:

| Component | Driver   |
| --------- | -------- |
| FastAPI   | asyncpg  |
| Alembic   | psycopg2 |

`alembic.ini`

```
postgresql+psycopg2://admin:admin123@localhost:5433/secRAG
```

---

# 16. Issue: Missing Imports in env.py

### Error

```
NameError: context not defined
```

### Fix

Add:

```python
from alembic import context
```

---

### Another Error

```
engine_from_config not defined
```

### Fix

Add:

```python
from sqlalchemy import engine_from_config
from sqlalchemy import pool
```

---

# 17. Alembic Migration Generated

Command:

```bash
uv run alembic revision --autogenerate -m "initial tables"
```

Generated migration:

```
alembic/versions/6a9e9e114623_initial_tables.py
```

---

# 18. Migration Applied

```bash
uv run alembic upgrade head
```

Alembic created tables and tracking table:

```
alembic_version
```

---

# Current System Status

Working components:

✔ FastAPI API
✔ Docker PostgreSQL
✔ Async SQLAlchemy
✔ Environment configuration
✔ Pydantic schemas
✔ CloudTrail ingestion
✔ Alembic migrations

---

# Next Planned Steps

### 1. Complete log ingestion

Implement pipelines for:

* GuardDuty logs
* VPC Flow logs

---

### 2. Security query indexes

Add indexes for investigation queries:

```
(event_time DESC)
(event_name, event_time)
(source_ip, event_time)
(user_name, event_time)
```

---

### 3. Unified security event layer

Create normalized event stream:

```
security_events
```

This will allow correlation between:

* CloudTrail
* GuardDuty
* Network logs

---

### 4. Vector embeddings

Add table:

```
log_embeddings
```

For RAG retrieval.

---

### 5. RAG security analyst

Goal:

```
Logs → embeddings → LLM reasoning → security report
```

Example query:

```
Show suspicious activity before DeleteBucket event
```

---

# Current Architecture

```
AWS Logs
    ↓
Ingestion Pipeline
    ↓
Postgres (structured + JSON logs)
    ↓
Vector embeddings
    ↓
RAG security analysis
```

---

# Status

**SecRAG backend foundation is now production-ready.**

Remaining work focuses on:

* ingestion scalability
* event correlation
* RAG reasoning layer
