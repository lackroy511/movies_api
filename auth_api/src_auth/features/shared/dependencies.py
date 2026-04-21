import jwt
from fastapi import Request

from src_auth.core.exc.exceptions import InvalidTokenOrExpiredTokenError
from src_auth.core.security.jwt import TokenPayload, verify_token


def get_current_user_payload(request: Request) -> TokenPayload:
    access_token = request.cookies.get("access_token")
    error_message = "Invalid or expired token"
    if not access_token:
        raise InvalidTokenOrExpiredTokenError(error_message)

    try:
        return verify_token(access_token, "access")
    except jwt.PyJWTError, ValueError:
        raise InvalidTokenOrExpiredTokenError("Invalid or expired token") from None