import logging
from fastapi import FastAPI

from src_api.api.router import router as main_router
from src_api.core.config.lifespan import lifespan
from src_api.core.exc.handlers import setup_exception_handlers

log = logging.getLogger(__name__)

app = FastAPI(
    title="Movies API",
    docs_url="/api/movies/doc/",
    openapi_url="/api/movies/doc/openapi.json",
    description="Movies API.",
    version="1.0.0",
    lifespan=lifespan,
)
app.include_router(main_router)

setup_exception_handlers(app)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8010)
