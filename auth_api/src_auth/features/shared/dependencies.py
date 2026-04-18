from fastapi import HTTPException, Request, status

from src_auth.core.security.jwt import TokenData, verify_token


def get_current_user(request: Request) -> TokenData:
    access_token = request.cookies.get("access_token")
    error_message = [{"msg": "Invalid or expired token"}]

    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_message,
        )

    payload = verify_token(access_token, "access")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_message,
        )

    return payload
