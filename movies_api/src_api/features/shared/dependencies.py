from src_api.core.exc.exceptions import UnauthorizedError
from src_api.features.shared.types import RolesType
import jwt
from src_api.core.security.jwt import verify_token
from fastapi import Request


async def get_current_user_roles(
    request: Request,
) -> list[RolesType]:
    access_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")
    if not access_token and not refresh_token:
        return []

    if not access_token and refresh_token:
        raise UnauthorizedError("Access token is required")
    
    if access_token and not refresh_token:
        raise UnauthorizedError("Refresh token is required") 
    
    try:
        verify_token(refresh_token, "refresh")  # ty: ignore
        payload = verify_token(access_token, "access")  # ty: ignore
        return payload.user_roles
    except jwt.PyJWTError, ValueError:
        raise UnauthorizedError("Invalid token or expired token.") from None
