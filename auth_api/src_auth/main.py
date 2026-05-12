import logging
from typing import Callable

from fastapi import FastAPI, Request, Response, status
from fastapi.responses import JSONResponse
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from src_auth.api.router import router as main_router
from src_auth.core.config.lifespan import lifespan
from src_auth.core.exc.handlers import register_exception_handlers

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
register_exception_handlers(app)
FastAPIInstrumentor.instrument_app(app)


@app.middleware("http")
async def before_request(request: Request, call_next: Callable) -> Response:
    request_id = request.headers.get("X-Request-Id")
    if not request_id:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "X-Request-Id is required"},
        )

    span = trace.get_current_span()
    span.set_attribute("http.request_id", request_id)
    return await call_next(request)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8020)
