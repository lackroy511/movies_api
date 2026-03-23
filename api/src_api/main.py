from fastapi import FastAPI

from src_api.api.router import router as main_router
from src_api.core.config.lifespan import lifespan

app = FastAPI(
    title="Movies API",
    docs_url="/api/doc/",
    description="Апи для получения информации о фильмах.",
    version="1.0.0",
    lifespan=lifespan,
)
app.include_router(main_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8010)
