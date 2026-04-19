import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src_auth.core.exc.exceptions import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
    UserNotFoundError,
)

log = logging.getLogger(__name__)


async def unexpected_error_handler(request: Request, exc: Exception) -> JSONResponse:
    log.error("Unexpected error", exc_info=exc)
    return JSONResponse(status_code=500, content={"detail": "Unexpected server error"})


async def user_already_exists_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": "User already exists"})


async def user_not_found_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": "User not found"})


async def invalid_credentials_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=401, content={"detail": "Invalid credentials"})


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(Exception, unexpected_error_handler)
    app.add_exception_handler(UserAlreadyExistsError, user_already_exists_handler)
    app.add_exception_handler(UserNotFoundError, user_not_found_handler)
    app.add_exception_handler(InvalidCredentialsError, invalid_credentials_handler)
