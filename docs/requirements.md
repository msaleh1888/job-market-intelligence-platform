# Job Market Intelligence Platform (JMIP) – Requirements

## 1. Overview

The Job Market Intelligence Platform (JMIP) is a backend-first system designed to continuously collect, normalize, and analyze job postings from multiple platforms in order to produce personalized job recommendations and actionable job market insights.

JMIP operates on two primary cadences:

- **Daily:** Identify and rank job opportunities that best match a defined user profile and portfolio, and provide clear application guidance.
- **Weekly:** Analyze aggregated job data to extract market trends, skill demand, competition signals, and skill gaps relative to the user profile.

The system is intentionally designed as a **data-driven backend platform**, with AI-assisted enrichment used as an optional augmentation layer. All core analytics, rankings, and reports are derived from persisted structured data to ensure reliability, reproducibility, and explainability.

---

## 2. Goals

The primary goals of JMIP are:

- Continuously collect job postings relevant to targeted roles.
- Persist job data in a normalized, queryable form with historical tracking.
- Generate daily ranked job recommendations tailored to a user profile.
- Provide explainable reasoning for each recommendation.
- Produce weekly job market analysis reports based on aggregated data.
- Identify skill gaps between market demand and the user’s existing skill set.
- Recommend skills and portfolio projects to address identified gaps.

---

## 3. Non-Goals

JMIP explicitly does **not** aim to:

- Automatically apply to jobs on behalf of the user.
- Guarantee job availability or hiring outcomes.
- Provide real-time analytics or streaming dashboards.
- Operate as a public or general-purpose job board.
- Depend on large language models (LLMs) for real-time decision-making or analytics.

---

## 4. Users and Scope

### Primary Scope
- A single-user system designed to support an individual job seeker targeting backend, full-stack, and AI-adjacent roles.

### Future Scope
- The system design should not prevent future multi-user expansion; however, multi-tenancy is not a requirement for the initial version.

---

## 5. Functional Requirements

### 5.1 Job Discovery and Ingestion
- The system shall support ingesting job postings from multiple platforms.
- The system shall allow configurable keyword-based searches per platform.
- The system shall support manual ingestion mechanisms (e.g., uploaded job exports).
- The system shall be extensible to support additional job platforms in the future.

### 5.2 Job Normalization and Storage
- The system shall normalize job postings into a canonical schema.
- The system shall deduplicate repeated job postings.
- The system shall track changes to job postings over time (e.g., applicant count, description updates).
- The system shall persist both raw and structured representations of job data.

### 5.3 Job Enrichment
- The system shall extract structured attributes from job descriptions, including:
  - Role category
  - Seniority level
  - Years of experience
  - Required and optional skills
  - Salary information when available
- The system shall support AI-assisted enrichment as an optional enhancement.
- The system shall continue operating when AI-assisted enrichment is unavailable.

### 5.4 Daily Recommendations
- The system shall generate daily job recommendations ranked by relevance to the user profile.
- The system shall explain why each job is recommended.
- The system shall identify potential risks or mismatches for each recommendation.
- The system shall provide guidance on how a CV or portfolio should be tailored for each job.

### 5.5 Weekly Market Analysis
- The system shall generate weekly aggregated job market reports.
- The system shall identify:
  - Most common job roles
  - Most in-demand skills
  - Roles with lowest apparent competition (when data is available)
- The system shall perform gap analysis between market demand and the user profile.
- The system shall recommend skills and portfolio projects to address identified gaps.

---

## 6. Non-Functional Requirements

### 6.1 Reliability
- The system shall be resilient to partial failures.
- Long-running operations shall be executed asynchronously.
- Failures shall not corrupt persisted data.

### 6.2 Idempotency
- Ingestion and enrichment operations shall be idempotent.
- Reprocessing the same job data shall not create duplicates or inconsistent state.

### 6.3 Observability
- The system shall emit structured logs for key events.
- The system shall expose metrics for throughput, failures, and latency.
- The system shall support tracing for asynchronous workflows.

### 6.4 Explainability
- Job recommendations and analyses shall be explainable based on persisted data.
- The system shall avoid opaque, non-reproducible decision-making.

### 6.5 Cost Control
- AI-assisted components shall be rate-limited and bounded.
- The system shall remain operational if AI-assisted components are unavailable.

---

## 7. Constraints and Assumptions

- Job data availability and quality depend on external platforms.
- Some attributes (e.g., salary, applicant count) may be missing or unreliable.
- AI-assisted enrichment may be probabilistic and imperfect.
- Deterministic data processing is preferred wherever possible.

---

## 8. Success Criteria

The system is considered successful if:

- Job data can be ingested and persisted on a daily basis without manual intervention.
- Daily job recommendations are produced with clear, explainable reasoning.
- Weekly job market reports can be generated reproducibly.
- The system continues to function when AI-assisted enrichment is disabled.
- System behavior can be understood and diagnosed using persisted state, logs, metrics, and traces.
