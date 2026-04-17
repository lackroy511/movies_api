from fastapi import APIRouter

router = APIRouter(prefix="/v1", tags=["Users V1"])


@router.get("/users/me")
async def get_current_user() -> dict:
    return {"message": "Get current user success"}


@router.patch("/users/me/change-email")
async def change_email() -> dict:
    return {"message": "Change email success"}


@router.patch("/users/me/change-password")
async def change_password() -> dict:
    return {"message": "Change password success"}


@router.get("/users/me/auth-history")
async def get_auth_history() -> dict:
    return {"message": "Get auth history success"}
