import jwt
from fastapi import Request

from src_api.core.config.settings import settings
from src_api.core.exc.exceptions import UnauthorizedError
from src_api.core.security.jwt import verify_token
from src_api.features.shared.types import RolesType


async def get_current_user_roles(
    request: Request,
) -> list[RolesType]:
    access_token = request.cookies.get(settings.access_cookie_name)
    refresh_token = request.cookies.get(settings.refresh_cookie_name)
    if not access_token and not refresh_token:
        return []

    if not access_token and refresh_token:
        raise UnauthorizedError("Access token is required")

    if access_token and not refresh_token:
        raise UnauthorizedError("Refresh token is required")

    try:
        verify_token(
            refresh_token,  # ty: ignore
            "refresh",
        )
        payload = verify_token(
            access_token,  # ty: ignore
            "access",
        )
        return payload.user_roles
    except (jwt.PyJWTError, ValueError):
        raise UnauthorizedError("Invalid token or expired token.") from None
