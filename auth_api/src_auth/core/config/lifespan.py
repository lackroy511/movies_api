from src_auth.core.config.logger import configure_logging
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    try:
        configure_logging()
        log.info("Auth API is starting...")
        yield
    finally:
        log.info("Auth API is shutting down...")
