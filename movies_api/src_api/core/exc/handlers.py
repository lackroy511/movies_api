import logging
import elasticsearch
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from elasticsearch.exceptions import NotFoundError

from src_api.core.exc.exceptions import UnauthorizedError, ForbiddenError

log = logging.getLogger(__name__)


async def elastic_not_found_handler(request: Request, exc: Exception) -> JSONResponse:
    if not isinstance(exc, elasticsearch.exceptions.NotFoundError):
        raise exc

    if exc.message == "index_not_found_exception":
        return JSONResponse(
            status_code=500,
            content={"detail": "Elastic index not found error"},
        )

    raise exc


async def unauthorized_error_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=401, content={"detail": "Unauthorized error"})


async def unexpected_error_handler(request: Request, exc: Exception) -> JSONResponse:
    log.error("Unexpected error", exc_info=exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "Unexpected server error"},
    )


async def forbidden_error_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=403, content={"detail": "Forbidden error"})


def setup_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(Exception, unexpected_error_handler)
    app.add_exception_handler(NotFoundError, elastic_not_found_handler)
    app.add_exception_handler(UnauthorizedError, unauthorized_error_handler)
    app.add_exception_handler(ForbiddenError, forbidden_error_handler)
