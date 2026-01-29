from collections.abc import AsyncGenerator

from fastapi import HTTPException
from fastapi.testclient import TestClient
from jmip_api.main import create_app
from sqlalchemy.ext.asyncio import AsyncSession


async def broken_db_session() -> AsyncGenerator[AsyncSession, None]:
    # Simulate a DB outage in a deterministic way
    raise HTTPException(status_code=503, detail="Database unavailable")
    yield  # pragma: no cover


def test_health_db_when_db_down_returns_503_with_standard_error_schema():
    app = create_app()

    # Override the dependency used by /health/db
    from jmip_api.core.dependencies import get_db_session

    app.dependency_overrides[get_db_session] = broken_db_session

    client = TestClient(app)
    resp = client.get("/health/db")

    assert resp.status_code == 503
    assert resp.json() == {
        "error": {
            "code": "HTTP_ERROR",
            "message": "Database unavailable",
            "details": {"path": "/health/db"},
        }
    }
