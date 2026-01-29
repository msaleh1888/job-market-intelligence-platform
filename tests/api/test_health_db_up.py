import os

import pytest
from fastapi.testclient import TestClient
from jmip_api.main import create_app


@pytest.mark.integration
def test_health_db_when_db_up_returns_ok():
    # Allow overriding DB URL for CI/local runs
    db_url = os.environ.get("JMIP_DATABASE_URL")
    if not db_url:
        pytest.skip("JMIP_DATABASE_URL not set; skipping integration test")

    app = create_app()
    client = TestClient(app)

    resp = client.get("/health/db")

    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
