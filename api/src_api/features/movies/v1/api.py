from fastapi import APIRouter

router = APIRouter(prefix="/v1/movies", tags=["V1 Movies"])


@router.get("/")
async def root() -> dict:
    return {"message": "Hello From V1 Movies"}