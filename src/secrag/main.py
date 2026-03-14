from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from secrag.core.database import get_db
from secrag.core.init_db import init_db
from secrag.ingestion.cloudtrail_ingest import ingest_cloudtrail_file
from secrag.ingestion.guardduty_ingest import ingest_guardduty_file
from secrag.ingestion.vpc_flow_ingest import ingest_vpc_flow_file

from strawberry.fastapi import GraphQLRouter

from secrag.graphql.schema import schema
from secrag.core.database import get_db
from secrag.ingestion.worker import run_ingestion
import asyncio

app = FastAPI(title="SecRAG")


@app.get("/")
async def health():
    return {"status": "SecRAG running"}


@app.get("/db-test")
async def db_test(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT 1"))
    return {"db": result.scalar()}

@app.get("/init-db")
async def initialize_db():
    await init_db()
    return {"status": "tables created"}


@app.get("/ingest/cloudtrail")
async def ingest_cloudtrail(db: AsyncSession = Depends(get_db)):

    file_path = "docs/cloudtrail_logs.json"

    count = await ingest_cloudtrail_file(file_path, db)

    return {"inserted": count}

@app.get("/ingest/guardduty")
async def ingest_guardduty(db: AsyncSession = Depends(get_db)):

    file_path = "docs/guardduty_findings.json"

    count = await ingest_guardduty_file(file_path, db)

    return {"inserted": count}


@app.get("/ingest/vpcflow")
async def ingest_vpcflow(db: AsyncSession = Depends(get_db)):

    file_path = "docs/vpc_flow_logs.log"

    count = await ingest_vpc_flow_file(file_path, db)

    return {"inserted": count}


async def get_context(db=Depends(get_db)):
    return {"db": db}

graphql_app = GraphQLRouter(
    schema,
    context_getter=get_context
)

app.include_router(graphql_app, prefix="/graphql")


@app.on_event("startup")
async def start_background_worker():

    asyncio.create_task(run_ingestion())