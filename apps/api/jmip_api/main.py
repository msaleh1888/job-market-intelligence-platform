import logging

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from jmip_api.core.config import settings
from jmip_api.core.errors import (
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from jmip_api.routers.health import router as health_router
from jmip_api.routers.health_db import router as health_db_router
from jmip_api.routers.version import router as version_router


def configure_logging() -> None:
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )


def create_app() -> FastAPI:
    # Startup phase
    configure_logging()

    logging.getLogger(__name__).info(
        "Starting JMIP API",
        extra={"env": settings.env},
    )

    app = FastAPI(
        title="JMIP API",
        version=settings.version,
    )

    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)

    app.include_router(health_router)
    app.include_router(version_router)
    app.include_router(health_db_router)

    return app


app = create_app()
