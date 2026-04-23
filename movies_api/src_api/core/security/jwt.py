from src_api.features.shared.types import RolesType
from datetime import datetime
from typing import Literal

import jwt
from pydantic import BaseModel

from src_api.core.config.settings import settings


TokenType = Literal["access", "refresh"]


class TokenPayload(BaseModel):
    user_id: str
    user_roles: list[RolesType]
    iat: datetime
    exp: datetime
    type: TokenType
    ver: int


def verify_token(token: str, token_type: TokenType) -> TokenPayload:
    payload = jwt.decode(
        token,
        settings.secret_key,
        algorithms=["HS256"],
    )
    if payload.get("type") != token_type:
        raise ValueError("Invalid token type")

    return TokenPayload(**payload)
