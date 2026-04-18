import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from src_auth.core.config.logger import configure_logging

from src_auth.core.db.cache import client as redis_client
from src_auth.core.db.sql_alch import engine as sql_alch_engine


log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    try:
        configure_logging()
        log.info("Auth API is starting...")
        yield
    finally:
        await redis_client.close()
        await sql_alch_engine.dispose()
        log.info("Auth API is shutting down...")
