from datetime import datetime, timedelta, timezone
from typing import Literal

import jwt
from pydantic import BaseModel

from src_auth.core.config.settings import settings

TokenType = Literal["access", "refresh"]


class IncorrectTokenTypeError(Exception):
    pass


class TokenData(BaseModel):
    user_id: int
    user_role: str
    iat: datetime
    exp: datetime
    type: TokenType


def create_token(user_id: int, user_role: str, token_type: TokenType) -> str:
    if token_type == "access":
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.access_token_expire_minutes,
        )
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            days=settings.refresh_token_expire_days,
        )

    to_encode = TokenData(
        user_id=user_id,
        user_role=user_role,
        iat=datetime.now(timezone.utc),
        exp=expire,
        type=token_type,
    )
    return jwt.encode(
        to_encode.model_dump(),
        settings.secret_key,
        algorithm="HS256",
    )


def verify_token(token: str, token_type: TokenType) -> TokenData | None:
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=["HS256"],
        )
        if payload.get("type") != token_type:
            raise IncorrectTokenTypeError("Incorrect token type")

        if "exp" in payload and isinstance(payload["exp"], int):
            payload["exp"] = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)

        return TokenData(**payload)
    except (jwt.PyJWTError, ValueError):
        return None
