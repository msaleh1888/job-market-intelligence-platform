# Job Market Intelligence Platform (JMIP)

JMIP is a backend-first system that ingests job postings from multiple platforms, normalizes and enriches them into structured data, and generates explainable daily job recommendations and weekly market intelligence.

The system is designed with production-style concerns in mind: idempotent ingestion, asynchronous workflows, historical snapshots, observability, deterministic analytics, and optional AI-assisted enrichment. A thin web UI is included to demonstrate full-stack integration.

## Documentation
- [Requirements](docs/requirements.md)
- [Architecture](docs/architecture.md)
- [Data model](docs/data_model.md)
- [API contracts](docs/api_contracts.md)
- [UI spec](docs/ui_spec.md)

## Repo layout
- `apps/api`: FastAPI service (HTTP API)
- `apps/worker`: async worker service (pipelines, scheduled runs)
- `apps/web`: Next.js web UI
- `packages/jmip`: shared Python package (domain, pipelines, db)

## Current Status

Phase 1 (Foundation) is complete.

The project currently includes:
- Async FastAPI backend
- PostgreSQL persistence with SQLAlchemy
- Alembic migrations
- Core data model (jobs, snapshots, skills)
- Health checks and tests

Next phase will focus on job ingestion and normalization.

## Local Development (Backend)

Requirements:
- Python 3.11+
- Docker

Start Postgres:
```bash
cd apps/api
docker compose up -d
```

Run migrations:
```bash
alembic upgrade head
```

Run API:
```bash
PYTHONPATH=apps/api uvicorn jmip_api.main:app --reload
```