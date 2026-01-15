# Job Market Intelligence Platform (JMIP) – UI Specification

## 1. Purpose

This document defines the scope and structure of the JMIP web user interface.  
The UI is intentionally **thin and product-focused**, designed to demonstrate full-stack capability while keeping the backend as the primary source of truth.

The UI:
- Consumes existing backend APIs without duplicating business logic
- Surfaces daily recommendations and weekly insights clearly
- Prioritizes clarity, explainability, and operability over visual complexity

This UI mirrors the type of **internal dashboards and decision-support tools** commonly built by backend and full-stack engineers.

---

## 2. Design Principles

### 2.1 Thin frontend
- No heavy client-side business logic
- No complex state machines in the browser
- Backend APIs remain authoritative

### 2.2 Explainability-first
- Every recommendation and insight should be explainable in the UI
- Score breakdowns, evidence, and rationale must be visible

### 2.3 Read-heavy, write-light
- Most pages are read-only views
- Writes are limited to configuration and profile updates

### 2.4 Incremental enhancement
- UI works even if some backend features are unavailable
- Partial data is displayed with explicit indicators

---

## 3. Tech Stack (Recommended)

- **Framework:** Next.js (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS + shadcn/ui
- **Charts:** Recharts
- **Data fetching:** Native fetch or React Query
- **Auth (MVP):** API key via environment variable → request header

---

## 4. Application Structure

```
apps/web/
  app/
    layout.tsx
    page.tsx                 # Dashboard (home)
    jobs/
      page.tsx               # Jobs explorer
      [jobId]/
        page.tsx             # Job detail
    reports/
      weekly/
        page.tsx             # Weekly report
    profile/
      page.tsx               # User profile
    settings/
      keywords/
        page.tsx             # Keyword sets
  components/
    RecommendationCard.tsx
    ScoreBreakdown.tsx
    SkillBadge.tsx
    SnapshotChart.tsx
    LoadingState.tsx
    ErrorState.tsx
  lib/
    api.ts                   # Typed API client / fetch wrappers
    types.ts                 # Shared UI types
```

---

## 5. Pages and Responsibilities

### 5.1 Dashboard – Daily Recommendations (`/`)

**Purpose**
- Primary landing page
- Shows the most actionable output of the system

**API calls**
- `GET /recommendations/latest`

**Content**
- List of recommended jobs (ranked)
- For each job:
  - Title, company, platform
  - Total score
  - Key reasons for match
  - CV tailoring notes
  - Risk notes

**UI components**
- `RecommendationCard`
- `ScoreBreakdown` (expandable)
- `SkillBadge`

**States**
- Loading: spinner/skeleton
- Empty: “No recommendations generated yet”
- Partial: warning badge if enrichment incomplete

---

### 5.2 Jobs Explorer (`/jobs`)

**Purpose**
- Explore the underlying job corpus
- Enable inspection and debugging of ingestion/enrichment

**API calls**
- `GET /jobs`
- Filters applied via query parameters

**Filters**
- Platform
- Location type
- Seniority
- Keyword search
- Minimum score (optional)

**Content**
- Table or card list of jobs
- Key metadata: title, company, applicants count, last seen
- Link to job detail page

**UI components**
- Filter bar
- Paginated list
- `LoadingState`, `ErrorState`

---

### 5.3 Job Detail (`/jobs/{jobId}`)

**Purpose**
- Deep inspection of a single job
- Show enrichment evidence and history

**API calls**
- `GET /jobs/{jobId}`
- `GET /jobs/{jobId}/snapshots`

**Content**
- Full job description
- Extracted skills with evidence and confidence
- Enrichment status and timestamp
- Snapshot chart (e.g., applicants over time)

**UI components**
- `SkillBadge`
- `SnapshotChart`
- Expandable sections for raw vs enriched data

---

### 5.4 Weekly Report (`/reports/weekly`)

**Purpose**
- Market intelligence and strategic insight

**API calls**
- `GET /reports/weekly/latest`

**Content**
- Summary (rendered from markdown)
- Charts:
  - Top roles
  - Top skills
- Tables:
  - Lowest competition roles
  - Skill gap analysis
- Recommended projects/skills

**UI components**
- Charts (Recharts)
- Markdown renderer
- Callout panels for gaps and recommendations

---

### 5.5 Profile (`/profile`)

**Purpose**
- Maintain the structured user profile used for matching

**API calls**
- `GET /profile`
- `PUT /profile`

**Content**
- Skills list with proficiency levels
- Portfolio projects (title, highlights, links)

**UI behavior**
- Simple edit forms
- Explicit save actions
- Optimistic UI optional (not required)

---

### 5.6 Keyword Sets (`/settings/keywords`)

**Purpose**
- Control discovery strategy without code changes

**API calls**
- `GET /keywords`
- `POST /keywords`
- `PUT /keywords/{id}`

**Content**
- List of keyword sets
- Platform association (or global)
- Active/inactive toggle

**Notes**
- Changes affect future ingestion runs only

---

## 6. Error and Loading States

All pages must handle:

- **Loading**
  - Skeletons or spinners
- **Errors**
  - API error messages surfaced clearly
- **Partial data**
  - Explicit badges indicating missing enrichment or incomplete fields

The UI must never silently fail.

---

## 7. Data Ownership and Boundaries

- The UI does not infer or compute business logic
- Scoring, analytics, and enrichment logic live exclusively in the backend
- The UI renders backend-provided explanations and metadata verbatim

This enforces a clean separation of concerns.

---

## 8. Accessibility and UX

- Keyboard navigation supported
- Readable typography and spacing
- Clear visual hierarchy
- No unnecessary animations

---

## 9. Non-Goals (UI)

The UI explicitly does **not** aim to:

- Automatically apply to jobs
- Provide real-time updates via websockets
- Implement complex authentication flows
- Serve as a public-facing consumer product

---

## 10. Success Criteria

The UI is considered successful if:

- A reviewer can understand system value within 2–3 minutes
- Daily recommendations and weekly reports are easily discoverable
- Job details and enrichment evidence are transparent
- The UI remains usable with partial or missing enrichment
- The project clearly demonstrates full-stack integration without overengineering
