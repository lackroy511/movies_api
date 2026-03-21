from fastapi import FastAPI
from src_api.api.router import router as main_router


app = FastAPI(
    title="Movies API",
    docs_url="/api/doc/",
    description="Апи для получения информации о фильмах.",
    version="1.0.0",
)
app.include_router(main_router)


@app.get("/", tags=["Root"])
async def root() -> dict:
    return {"message": "Hello World"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8010)
