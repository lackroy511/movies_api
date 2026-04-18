import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src_auth.api.router import router as main_router
from src_auth.core.config.lifespan import lifespan

log = logging.getLogger(__name__)

app = FastAPI(
    title="Auth API",
    docs_url="/api/auth/doc/",
    openapi_url="/api/auth/doc/openapi.json",
    description="Auth API.",
    version="1.0.0",
    lifespan=lifespan,
)
app.include_router(main_router)


@app.exception_handler(Exception)
async def unexpected_error_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    try:
        raise exc
    except Exception:
        log.exception("Unexpected error")
    
    return JSONResponse(
        status_code=500,
        content={"detail": "Unexpected server error"},
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8020)
