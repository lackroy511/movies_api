from typing import Annotated

from fastapi import Depends, Request

from src_auth.core.config.settings import RolesType, settings
from src_auth.core.exc.exceptions import (
    AccessDeniedError, InvalidTokenOrExpiredTokenError,
)
from src_auth.core.security.jwt import TokenPayload
from src_auth.features.auth.v1.service import SessionService, get_session_service


class RequireRole:
    def __init__(self, allowed_roles: list[RolesType]) -> None:
        self.allowed_roles = allowed_roles

    def __call__(
        self,
        token_payload: Annotated[TokenPayload, Depends(get_current_user_payload)],
    ) -> None:
        user_roles = getattr(token_payload, "user_roles", [])

        has_access = bool(set(user_roles) & set(self.allowed_roles))
        if not has_access:
            raise AccessDeniedError("Access denied")


async def get_current_user_payload(
    request: Request,
    session_service: Annotated[
        SessionService,
        Depends(get_session_service),
    ],
) -> TokenPayload:
    access_token = request.cookies.get(settings.access_cookie_name)
    if not access_token:
        raise InvalidTokenOrExpiredTokenError("Access token not found")
    
    payload = session_service.decode_token(access_token, "access")
    await session_service.verify_session(payload, access_token)
    return payload
