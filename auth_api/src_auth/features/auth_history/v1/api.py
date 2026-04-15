from uuid import UUID

from fastapi import APIRouter

router = APIRouter(prefix="/v1", tags=["Auth history"])


@router.get("/auth-history/me")
async def get_auth_history() -> dict:
    return {"message": "Get auth history success"}


@router.get("/auth-history/{user_id:uuid}")
async def get_user_auth_history(user_id: UUID) -> dict:
    return {"message": f"Get user {user_id} auth history success"}
