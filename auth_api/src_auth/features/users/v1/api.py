from fastapi import APIRouter

router = APIRouter(prefix="/v1", tags=["Users"])


@router.get("/users/me")
async def get_current_user() -> dict:
    return {"message": "Get current user success"}


@router.post("/users/change-email")
async def change_email() -> dict:
    return {"message": "Change email success"}


@router.post("/users/change-password")
async def change_password() -> dict:
    return {"message": "Change password success"}
