from src_auth.features.auth.v1.service import AuthService, get_auth_service
from typing import Annotated
from src_auth.features.auth.v1.schemas import RegisterRequest, RegisteredUserResponse
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/v1", tags=["Auth V1"])


@router.post("/register")
async def register(
    user_data: RegisterRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> RegisteredUserResponse:
    new_user = await auth_service.register_user(
        email=user_data.email,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        password=user_data.password,
    )
    return RegisteredUserResponse.model_validate(new_user)


@router.post("/login")
async def login() -> dict:
    return {"message": "Login success"}


@router.post("/refresh")
async def refresh() -> dict:
    return {"message": "Refresh success"}


@router.post("/logout")
async def logout() -> dict:
    return {"message": "Logout success"}


@router.post("/logout-all")
async def logout_all() -> dict:
    return {"message": "Logout all success"}
