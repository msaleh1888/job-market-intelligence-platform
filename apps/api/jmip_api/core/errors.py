import logging
from typing import Any

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


def error_response(
    code: str,
    message: str,
    details: dict[str, Any] | None = None,
    status_code: int = 400,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "message": message, "details": details or {}}},
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    return error_response(
        code="HTTP_ERROR",
        message=str(exc.detail),
        details={"path": str(request.url.path)},
        status_code=exc.status_code,
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    return error_response(
        code="VALIDATION_ERROR",
        message="Request validation failed",
        details={"path": str(request.url.path), "errors": exc.errors()},
        status_code=422,
    )


logger = logging.getLogger(__name__)


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    # Log full exception server-side (stack trace), return safe message to client
    logger.exception("Unhandled exception", extra={"path": str(request.url.path)})
    return error_response(
        code="INTERNAL_ERROR",
        message="Internal server error",
        details={"path": str(request.url.path)},
        status_code=500,
    )
