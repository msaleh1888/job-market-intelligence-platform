# Job Market Intelligence Platform (JMIP) – API Contracts

## 1. Purpose

This document defines the external API surface for JMIP. It is intended to be:

- Clear enough for a frontend (and future clients) to integrate against
- Stable enough to treat as a contract during implementation
- Explicit about errors, idempotency expectations, and async execution

JMIP is designed as a backend-first system. Many operations enqueue background jobs and return immediately with a run identifier.

> Note: Endpoint paths and schemas may evolve during implementation, but the semantics defined here are the source of truth.

---

## 2. Conventions

### 2.1 Base URL
- `/api` prefix is optional. For simplicity, examples omit it (e.g., `POST /ingest/upload`).

### 2.2 Content types
- Requests and responses use `application/json` unless otherwise specified (file upload endpoints use `multipart/form-data`).

### 2.3 Identifiers
- `job_id`, `run_id`, and `report_id` are opaque string/UUID identifiers.

### 2.4 Timestamps
- ISO-8601 format (UTC) unless otherwise specified.

### 2.5 Pagination
List endpoints support:
- `limit` (default 50, max 200)
- `offset` (default 0)

### 2.6 Error format
All errors follow:

```json
{
  "error": {
    "code": "STRING_CODE",
    "message": "Human readable message",
    "details": { "optional": "context" }
  }
}
```

---

## 3. Health and Metadata

### 3.1 Health check
**GET** `/health`

**200 OK**
```json
{ "status": "ok" }
```

### 3.2 Version
**GET** `/version`

**200 OK**
```json
{
  "name": "jmip",
  "version": "0.1.0",
  "commit": "optional"
}
```

---

## 4. Ingestion

### 4.1 Upload job export (MVP ingestion path)
**POST** `/ingest/upload`

Uploads an export file (CSV or JSON) from a supported platform.

- Content-Type: `multipart/form-data`
- Form fields:
  - `platform` (string, required): `linkedin` | `upwork` | others later
  - `file` (required): CSV or JSON
  - `source_label` (optional): free-text label for provenance (e.g., “LinkedIn saved search export”)

**Response**
- **202 Accepted** (ingestion queued)
```json
{
  "ingest_run_id": "run_123",
  "status": "queued"
}
```

**Errors**
- 400 `INVALID_INPUT` (bad platform, unsupported file)
- 413 `PAYLOAD_TOO_LARGE`

---

### 4.2 Ingest raw payload (connector-facing)
**POST** `/ingest/raw`

Used by automated connectors to send raw job payloads directly.

**Request**
```json
{
  "platform": "linkedin",
  "fetched_at": "2026-01-15T10:00:00Z",
  "items": [
    {
      "external_id": "optional",
      "source_url": "optional",
      "raw_payload": { "any": "json" },
      "raw_text": "optional extracted text"
    }
  ]
}
```

**202 Accepted**
```json
{ "ingest_run_id": "run_124", "status": "queued" }
```

---

### 4.3 Get ingestion run status
**GET** `/ingest/runs/{ingest_run_id}`

**200 OK**
```json
{
  "ingest_run_id": "run_123",
  "status": "running",
  "created_at": "2026-01-15T10:01:00Z",
  "stats": {
    "items_received": 120,
    "items_normalized": 98,
    "jobs_created": 40,
    "jobs_updated": 58,
    "duplicates_skipped": 22,
    "errors": 0
  }
}
```

---

## 5. Jobs

### 5.1 List jobs
**GET** `/jobs`

**Query parameters (optional)**
- `platform` (string)
- `location_type` (`remote|hybrid|onsite|unknown`)
- `seniority` (`intern|junior|mid|senior|staff|lead|unknown`)
- `min_score` (number, filters by latest recommendation score if available)
- `updated_after` (ISO timestamp)
- `q` (string; basic keyword search over title/company)

**200 OK**
```json
{
  "items": [
    {
      "job_id": "job_1",
      "platform": "linkedin",
      "title": "Backend Engineer (Python)",
      "company": "Example Co",
      "location_text": "Remote - EMEA",
      "location_type": "remote",
      "seniority": "mid",
      "years_min": 2,
      "years_max": 5,
      "salary_min": null,
      "salary_max": null,
      "salary_currency": null,
      "salary_period": "unknown",
      "applicants_count": 43,
      "first_seen_at": "2026-01-10T09:00:00Z",
      "last_seen_at": "2026-01-15T09:00:00Z",
      "is_active": true
    }
  ],
  "limit": 50,
  "offset": 0,
  "total": 1
}
```

---

### 5.2 Get job details
**GET** `/jobs/{job_id}`

**200 OK**
```json
{
  "job_id": "job_1",
  "platform": "linkedin",
  "source_url": "https://…",
  "external_id": "optional",
  "title": "Backend Engineer (Python)",
  "company": { "name": "Example Co", "website": null },
  "location_text": "Remote - EMEA",
  "location_type": "remote",
  "country": null,
  "seniority": "mid",
  "years_min": 2,
  "years_max": 5,
  "salary_min": null,
  "salary_max": null,
  "salary_currency": null,
  "salary_period": "unknown",
  "applicants_count": 43,
  "posted_at": null,
  "description_text": "…",
  "first_seen_at": "2026-01-10T09:00:00Z",
  "last_seen_at": "2026-01-15T09:00:00Z",
  "is_active": true,
  "enrichment": {
    "status": "partial",
    "updated_at": "2026-01-15T10:20:00Z",
    "skills": [
      {
        "name": "FastAPI",
        "category": "backend",
        "importance": "must",
        "confidence": 0.88,
        "source": "ai",
        "evidence": "Experience building APIs with FastAPI…"
      }
    ]
  }
}
```

---

### 5.3 Get job snapshots
**GET** `/jobs/{job_id}/snapshots`

**200 OK**
```json
{
  "job_id": "job_1",
  "items": [
    {
      "snapshot_at": "2026-01-10T09:00:00Z",
      "applicants_count": 10,
      "salary_min": null,
      "salary_max": null,
      "salary_currency": null,
      "salary_period": "unknown",
      "description_hash": "sha256:…"
    },
    {
      "snapshot_at": "2026-01-15T09:00:00Z",
      "applicants_count": 43,
      "salary_min": null,
      "salary_max": null,
      "salary_currency": null,
      "salary_period": "unknown",
      "description_hash": "sha256:…"
    }
  ]
}
```

---

### 5.4 Trigger enrichment for a job
**POST** `/jobs/{job_id}/enrich`

Enqueues enrichment for a given job. This endpoint is **idempotent**: if enrichment is already up-to-date, the system may return an immediate `no_op`.

**202 Accepted**
```json
{ "enrich_run_id": "run_200", "status": "queued" }
```

**200 OK** (no-op)
```json
{ "enrich_run_id": null, "status": "no_op" }
```

---

### 5.5 Get enrichment run status
**GET** `/enrich/runs/{enrich_run_id}`

**200 OK**
```json
{
  "enrich_run_id": "run_200",
  "job_id": "job_1",
  "status": "success",
  "created_at": "2026-01-15T10:05:00Z",
  "finished_at": "2026-01-15T10:06:30Z",
  "stats": {
    "rules_parsed": true,
    "llm_used": true,
    "skills_extracted": 12,
    "validation_passed": true,
    "retries": 1
  }
}
```

---

## 6. Recommendations

### 6.1 Run daily recommendations
**POST** `/recommendations/run`

Enqueues a recommendation run for a given date (defaults to today).

**Request**
```json
{ "date": "2026-01-15", "limit": 20 }
```

**202 Accepted**
```json
{ "recommendation_run_id": "run_300", "status": "queued" }
```

---

### 6.2 Get latest recommendations
**GET** `/recommendations/latest`

**200 OK**
```json
{
  "recommendation_run_id": "run_300",
  "run_date": "2026-01-15",
  "generated_at": "2026-01-15T11:00:00Z",
  "items": [
    {
      "rank": 1,
      "job_id": "job_1",
      "title": "Backend Engineer (Python)",
      "company": "Example Co",
      "platform": "linkedin",
      "score_total": 0.86,
      "score_breakdown": {
        "skill_overlap": 0.55,
        "experience_fit": 0.15,
        "location_fit": 0.10,
        "recency": 0.06,
        "competition_penalty": -0.00
      },
      "why_match": [
        "Strong overlap on FastAPI, Docker, PostgreSQL",
        "Experience range aligns with requested 2–5 years",
        "Remote-friendly location"
      ],
      "cv_tailoring_notes": [
        "Emphasize FastAPI microservice work and Dockerized deployments",
        "Highlight production monitoring/logging experience"
      ],
      "risk_notes": [
        "Salary not listed; verify early in recruiter call"
      ]
    }
  ]
}
```

---

### 6.3 Get recommendations by run id
**GET** `/recommendations/{recommendation_run_id}`

Same schema as `/recommendations/latest`.

---

### 6.4 Compare recommendation runs (optional)
**GET** `/recommendations/compare?run_a=...&run_b=...`

Returns summary diffs (rank shifts, score changes). Useful for tuning scoring logic over time.

---

## 7. Reports

### 7.1 Run weekly report
**POST** `/reports/weekly/run`

**Request**
```json
{ "week_start": "2026-01-12" }
```

**202 Accepted**
```json
{ "weekly_report_id": "rep_100", "status": "queued" }
```

---

### 7.2 Get latest weekly report
**GET** `/reports/weekly/latest`

**200 OK**
```json
{
  "weekly_report_id": "rep_100",
  "week_start": "2026-01-12",
  "generated_at": "2026-01-15T12:00:00Z",
  "summary_markdown": "## Weekly Summary\n…",
  "report": {
    "top_roles": [
      { "role": "Backend Engineer", "count": 42 },
      { "role": "Full-Stack Engineer", "count": 21 }
    ],
    "top_skills": [
      { "skill": "Python", "count": 55 },
      { "skill": "FastAPI", "count": 24 }
    ],
    "competition": {
      "lowest_applicants_roles": [
        { "role": "Backend Engineer", "median_applicants": 18 }
      ]
    },
    "gap_analysis": {
      "missing_high_demand_skills": [
        { "skill": "PostgreSQL", "reason": "Frequently required in backend roles" }
      ],
      "recommended_projects": [
        {
          "title": "Production FastAPI + Postgres Service",
          "skills_covered": ["PostgreSQL", "Alembic", "Async jobs"],
          "notes": "Build CRUD + background enrichment and deploy with CI."
        }
      ]
    }
  }
}
```

---

### 7.3 Get weekly report by id
**GET** `/reports/weekly/{weekly_report_id}`

Same schema as `/reports/weekly/latest`.

---

## 8. Profile and Configuration

### 8.1 Get user profile
**GET** `/profile`

**200 OK**
```json
{
  "profile_id": "me",
  "skills": [
    { "name": "FastAPI", "level": "intermediate" },
    { "name": "Docker", "level": "intermediate" }
  ],
  "projects": [
    {
      "title": "RAG Microservice",
      "highlights": ["FastAPI endpoint", "Vector search"],
      "links": { "github": "https://…" }
    }
  ],
  "updated_at": "2026-01-10T12:00:00Z"
}
```

---

### 8.2 Update user profile
**PUT** `/profile`

**Request**
```json
{
  "skills": [
    { "name": "FastAPI", "level": "intermediate" },
    { "name": "PostgreSQL", "level": "beginner" }
  ],
  "projects": [
    {
      "title": "JMIP",
      "highlights": ["Async ingestion", "Explainable recommendations"],
      "links": { "github": "https://…" }
    }
  ]
}
```

**200 OK**
```json
{ "status": "updated", "updated_at": "2026-01-15T12:10:00Z" }
```

---

### 8.3 List keyword sets
**GET** `/keywords`

**200 OK**
```json
{
  "items": [
    {
      "id": "kw_1",
      "name": "Backend – Python",
      "platform": null,
      "keywords": ["python backend", "fastapi", "postgresql", "redis"],
      "filters": { "remote": true },
      "is_active": true
    }
  ]
}
```

---

### 8.4 Create/update keyword sets
**POST** `/keywords`

**Request**
```json
{
  "name": "Backend – Python",
  "platform": null,
  "keywords": ["python backend", "fastapi", "postgresql", "redis"],
  "filters": { "remote": true },
  "is_active": true
}
```

**201 Created**
```json
{ "id": "kw_2" }
```

**PUT** `/keywords/{id}` updates an existing set.

---

## 9. Asynchronous Execution Semantics

### 9.1 General pattern
Operations that may take seconds/minutes return `202 Accepted` and a run identifier. Clients should poll the relevant `/runs/{id}` endpoint.

### 9.2 Idempotency expectations
- `POST /jobs/{job_id}/enrich` is idempotent (may return `no_op`).
- Recommendation and report runs may be treated as idempotent per (date/week_start, params). The system may reuse existing runs where applicable.

### 9.3 Partial results
JMIP supports partial enrichment:
- Jobs may be returned with incomplete enrichment and explicit `enrichment.status`.
- Analytics may exclude fields that are unavailable and indicate coverage in the report payload.

---

## 10. Authentication (MVP)

Initial versions may use:
- API key header (e.g., `X-API-Key`)
- or JWT (future)

Auth is intentionally minimal for the portfolio scope, but endpoints are designed to allow expansion.

---

## 11. Notes for Frontend Integration

A thin web UI is expected to integrate against:
- `GET /recommendations/latest`
- `GET /jobs` and `GET /jobs/{job_id}`
- `GET /reports/weekly/latest`
- `GET/PUT /profile`
- `GET/POST/PUT /keywords`

All responses are designed to be directly renderable and include human-friendly summaries where appropriate (e.g., `why_match`, `cv_tailoring_notes`, `summary_markdown`).
