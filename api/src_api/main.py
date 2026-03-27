from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src_api.api.router import router as main_router
from src_api.core.config.lifespan import lifespan

app = FastAPI(
    title="Movies API",
    docs_url="/api/doc/",
    openapi_url="/api/doc/openapi.json",
    description="Movies API.",
    version="1.0.0",
    lifespan=lifespan,
)
app.include_router(main_router)


@app.exception_handler(Exception)
async def unexpected_error_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={"detail": "Unexpected server error"},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8010)
