import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from src_api.core.db.cache import client as redis_client
from src_api.core.db.elastic_db import client as elastic_client

log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    try:
        yield
    finally:
        await elastic_client.close()
        await redis_client.close()
