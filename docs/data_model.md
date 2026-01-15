# Job Market Intelligence Platform (JMIP) – Data Model

## 1. Purpose

This document defines the conceptual data model for JMIP: the core entities, relationships, ownership of data, and why specific tables/fields exist. It is intended to support:

- A clean, normalized schema for job ingestion and analysis
- Idempotent ingestion and deduplication
- Historical tracking (snapshots) for trend analysis
- Explainable recommendations and reproducible weekly reporting
- Optional AI-assisted enrichment with provenance and confidence

> Note: This document is conceptual. Implementation details (ORM, migrations) are covered during implementation.

---

## 2. Core Concepts

### 2.1 Raw vs structured data
JMIP persists both:
- **Raw inputs** (payloads/text) for traceability and reprocessing
- **Structured outputs** (normalized tables) for reliable analytics and scoring

This supports debugging, model/prompt iteration, and reproducibility.

### 2.2 Current state vs history
JMIP stores:
- **Current job state** (latest known values)
- **Historical snapshots** when a job changes meaningfully over time (applicant count, description, salary)

This enables week-over-week trends and protects against data drift.

### 2.3 Provenance and confidence
For extracted/enriched fields, JMIP tracks:
- **source**: rules vs AI-assisted vs manual
- **confidence**: numeric score (0..1) where appropriate
- **evidence**: text snippets backing extracted skills

This supports explainability and operational debugging.

---

## 3. Entities and Relationships (Conceptual)

### 3.1 Platform
Represents an external source of jobs (e.g., LinkedIn, Upwork).

**Why it exists**
- Enables platform-specific connector behavior and filtering
- Supports future expansion without changing the schema

**Key fields**
- `name` (e.g., `linkedin`, `upwork`)

---

### 3.2 Search Keyword Set
Represents the configured search intent per platform (or global), including keywords and filters.

**Why it exists**
- Separates “what we search for” from code (configuration-as-data)
- Supports iteration on targeting roles and discovery strategy

**Key fields**
- `keywords` (list)
- `filters` (structured JSON; e.g., location, remote, time window)
- `platform_id` (nullable to apply globally)

---

### 3.3 Raw Job Post
Stores the raw payload and/or raw extracted text as ingested from a platform.

**Why it exists**
- Traceability: inspect original source inputs
- Reprocessing: rerun parsers/enrichment as logic evolves
- Forensics: debug connector changes or extraction errors

**Key fields**
- `platform_id`
- `source_url` (when available)
- `external_id` (when available)
- `raw_payload` (JSON)
- `raw_text` (plain text view of the posting)
- `content_hash` (for dedupe and idempotency)
- `fetched_at`

**Uniqueness / idempotency (recommended)**
- Prefer unique on `(platform_id, external_id)` when stable IDs exist
- Otherwise unique on `(platform_id, content_hash)` as a fallback

---

### 3.4 Company
Represents the hiring organization.

**Why it exists**
- Enables grouping analytics by company
- De-duplicates company information across jobs
- Supports future enrichment (company size, domain, etc.)

**Key fields**
- `name`
- `website` (optional)

---

### 3.5 Job (Canonical)
The canonical, normalized representation of a job posting.

**Why it exists**
- Forms the backbone for filtering, scoring, and reporting
- Acts as the “current state” view (latest known values)

**Key fields (typical)**
- Identity:
  - `platform_id`, `external_id` (optional), `source_url` (optional)
  - `company_id`
- Content:
  - `title`
  - `description_text`
- Location:
  - `location_text`
  - `location_type` (remote / hybrid / onsite / unknown)
  - `country` (optional)
- Seniority:
  - `seniority` (intern / junior / mid / senior / staff / lead / unknown)
  - `years_min`, `years_max` (optional)
- Compensation (optional):
  - `salary_min`, `salary_max`
  - `salary_currency`
  - `salary_period` (hour / month / year / unknown)
- Competition (optional):
  - `applicants_count`
- Lifecycle:
  - `posted_at` (optional)
  - `first_seen_at`
  - `last_seen_at`
  - `is_active`

**Notes**
- Fields may be partially known; nullability is expected.
- `first_seen_at/last_seen_at` support recency, freshness scoring, and deactivation.

---

### 3.6 Job Snapshot
A point-in-time record capturing meaningful changes to a job.

**Why it exists**
- Applicant counts and job descriptions change over time
- Snapshots allow time-series analysis and auditability
- Prevents overwriting history

**What triggers a snapshot**
- `applicants_count` change beyond a threshold (or any change if simple)
- `description_hash` changes
- salary fields change

**Key fields**
- `job_id`
- `snapshot_at`
- `applicants_count`
- salary fields (optional)
- `description_hash`
- `raw_job_post_id` (link to raw source for traceability)

---

### 3.7 Skill (Canonical)
Represents a normalized skill/technology concept (e.g., “FastAPI”, “PostgreSQL”, “Docker”).

**Why it exists**
- Enables robust aggregation and gap analysis
- Avoids string-matching chaos (“Postgres” vs “PostgreSQL”)
- Supports categorization (backend/cloud/llm/devops)

**Key fields**
- `name` (canonical)
- `category` (backend, cloud, devops, ml, llm, data, etc.)

---

### 3.8 Job Skill Mention (Association)
Connects a Job to a Skill, with importance and evidence.

**Why it exists**
- Enables skill frequency analytics and role-specific skill requirements
- Supports explainable matching (“this job requires X, user has X”)

**Key fields**
- `job_id`, `skill_id`
- `importance` (must / nice / unknown)
- `evidence` (snippet or bullet from job description)
- `confidence` (0..1)
- `source` (rules / ai / manual)

---

### 3.9 User Profile
Represents the user’s skills and portfolio as structured data.

**Why it exists**
- Matching and gap analysis require an explicit user profile model
- Enables CV tailoring suggestions grounded in portfolio items

**Key fields**
- `skills_json` (canonical skill list + optional proficiency levels)
- `projects_json` (project titles, tech stack, links, highlights)
- `updated_at`

**Notes**
- Initial scope is single-user; schema should not block future multi-user support.

---

### 3.10 Recommendation Run
A record of a daily recommendation generation execution.

**Why it exists**
- Recommendations should be reproducible and auditable
- Supports comparing ranking logic changes over time

**Key fields**
- `run_date`
- `params` (scoring weights/version, filters)
- `status`

---

### 3.11 Recommendation Item
The ranked job list produced by a Recommendation Run.

**Why it exists**
- Stores explainable results for UI and audit
- Enables “why” explanations and score transparency

**Key fields**
- `recommendation_run_id`, `job_id`
- `score_total`
- `score_breakdown` (structured JSON of feature contributions)
- `cv_tailoring_notes` (text)
- `risk_notes` (text)

---

### 3.12 Weekly Report
A persisted weekly market analysis artifact.

**Why it exists**
- Reports should be reproducible and shareable
- Enables UI display and historical comparisons

**Key fields**
- `week_start`
- `report_json` (aggregates, distributions, top skills, etc.)
- `summary_markdown` (human-readable report)
- `generated_at`

---

## 4. Derived Data and Computation Boundaries

### 4.1 Derived fields
Some fields are derived and may be recomputed:
- `role_category` / job family classification (if modeled)
- skill extraction results (can be re-run from `raw_text`)
- recommendation scores (computed from `job_skill` + `user_profile`)

### 4.2 Deterministic analytics boundary
Weekly “most demanded skills” should be computed deterministically from persisted structured data:

- Skill demand = aggregation over `job_skill`
- Role distributions = aggregation over job classifications (if stored)
- Competition = aggregation over `job_snapshot.applicants_count` (when available)

The LLM layer is used primarily to convert text into structured fields; analytics run without live LLM calls.

---

## 5. Idempotency and Deduplication Strategy (Data Model Perspective)

JMIP enforces idempotency at the data layer using:

1. **Stable identity when available**
   - Unique `(platform_id, external_id)`

2. **Fallback identity**
   - Normalized URL or `content_hash` (raw payload / text)

3. **Upserts**
   - Update `last_seen_at` and mutable fields
   - Insert snapshots for historical changes

4. **Snapshot tables**
   - Preserve history rather than overwriting

This ensures retries and repeated ingestion do not create duplicates or corrupt state.

---

## 6. Optional Extensions (Future)

The core model supports incremental additions, such as:

- **Document/RAG layer**
  - `document` table for stored text chunks
  - `embedding` table referencing vector storage IDs
- **Application tracking**
  - `application` table for applied/interview/offers status
- **Multi-tenancy**
  - add `user_id` and partition data, or add a tenant boundary later

---

## 7. Summary

JMIP’s data model is designed around durable, queryable “facts”:

- Raw inputs are stored for traceability.
- Canonical job records represent the current known state.
- Snapshots capture change over time.
- Skills are normalized into a canonical taxonomy for analytics and gap analysis.
- Recommendations and reports are persisted as auditable artifacts.

This structure enables reliable backend behavior, explainable outputs, and optional AI-assisted enrichment without making AI a single point of failure.
