from typing import Annotated
from uuid import UUID

import jwt
from fastapi import Depends, Request

from src_auth.core.exc.exceptions import InvalidTokenOrExpiredTokenError
from src_auth.core.security.jwt import TokenPayload, verify_token
from src_auth.features.auth.v1.repository import (
    TokenVersionRepoInterface,
    get_version_token_repository,
)


async def get_current_user_payload(
    request: Request,
    version_repo: Annotated[
        TokenVersionRepoInterface,
        Depends(get_version_token_repository),
    ],
) -> TokenPayload:
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise InvalidTokenOrExpiredTokenError("Token not found in cookies")

    try:
        payload = verify_token(access_token, "access")
    except jwt.PyJWTError, ValueError:
        raise InvalidTokenOrExpiredTokenError(
            "Invalid token or expired token",
        ) from None

    actual_ver = await version_repo.get_user_token_version(UUID(payload.user_id))
    if not actual_ver or payload.ver != actual_ver.version:
        raise InvalidTokenOrExpiredTokenError("Invalid token version")

    return payload
