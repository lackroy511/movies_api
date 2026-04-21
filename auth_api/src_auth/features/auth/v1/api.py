from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response

from src_auth.features.auth.v1.schemas import (
    LoginRequest,
    RegisterRequest,
    UserResponse, StatusResponse,
)
from src_auth.features.auth.v1.service import AuthService, get_auth_service

router = APIRouter(prefix="/v1", tags=["Auth V1"])


@router.post("/register")
async def register(
    user_data: RegisterRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> UserResponse:
    new_user = await auth_service.register_user(
        email=user_data.email,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        password=user_data.password,
    )
    return UserResponse.model_validate(new_user)


@router.post("/login")
async def login(
    request: Request,
    login_data: LoginRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    response: Response,
) -> UserResponse:
    logged_user = await auth_service.login_user(
        request=request,
        email=login_data.email,
        password=login_data.password,
        response=response,
    )
    return UserResponse.model_validate(logged_user)


@router.post("/refresh")
async def refresh(
    request: Request,
    response: Response,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> StatusResponse:
    await auth_service.refresh_tokens(request, response)
    return StatusResponse()


@router.post("/logout")
async def logout() -> dict:
    return {"message": "Logout success"}


@router.post("/logout-all")
async def logout_all() -> dict:
    return {"message": "Logout all success"}
