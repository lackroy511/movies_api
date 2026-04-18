import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src_auth.core.exc.exceptions import UserAlreadyExistsError

log = logging.getLogger(__name__)


async def user_already_exists_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": "User already exists"})


async def unexpected_error_handler(request: Request, exc: Exception) -> JSONResponse:
    log.error("Unexpected error", exc_info=exc)
    return JSONResponse(status_code=500, content={"detail": "Unexpected server error"})


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(UserAlreadyExistsError, user_already_exists_handler)
    app.add_exception_handler(Exception, unexpected_error_handler)
