# Antigravity Frontend Build Brief — Tab2PBI

Build a production-quality frontend for the existing Tab2PBI application. The backend already exists and must remain the source of truth.

## Product goal

Tab2PBI is a Tableau → Power BI migration assurance platform. It should feel like an enterprise migration control plane, not a developer utility and not a generic AI dashboard.

The primary user journey is:

`Home → New Migration → Upload Tableau asset → Assessment → Migration Plan → Run Migration → Validation/Results → Download Artifacts`

## Technical stack

Create the frontend inside `/frontend` using:

- React + TypeScript
- Vite
- Tailwind CSS
- React Router
- lightweight component architecture
- native fetch or a small typed API client

Do not replace the existing Python/FastAPI backend.

During local development, proxy API requests to `http://127.0.0.1:8000`.

## Existing backend APIs

- `GET /health`
- `GET /api/v1/engine/status`
- `POST /api/v1/analyze` — multipart form-data; field name `file`
- `POST /api/v1/migrate` — multipart form-data; field name `file`
- `GET /api/v1/jobs/{migration_id}`
- `GET /api/v1/jobs/{migration_id}/download`

Accepted source files: `.twb`, `.twbx`, `.tds`, `.tdsx`.

Before implementing UI models, inspect the real response schemas in `tab2pbi/models.py`, `tab2pbi/main.py`, `tab2pbi/orchestrator.py`, and `tab2pbi/assessment.py`. Do not invent response fields.

## UX direction

Use a restrained international enterprise design:

- clean light theme by default
- strong typography hierarchy
- compact but readable information density
- subtle borders and elevation
- no excessive gradients
- no giant empty cards
- no decorative illustrations that do not help migration work
- clear PASS / REVIEW / FAILED states
- use icons sparingly and consistently
- responsive desktop-first layout

The application should communicate trust, engineering control, validation and auditability.

## Navigation

Left sidebar or compact top/side hybrid navigation:

- Overview
- New Migration
- Migrations
- Validation / Review (may initially route into a migration detail page)
- Settings / Engine Status

If a backend feature is not yet available, show an honest empty/unavailable state rather than fake data.

## Required screens

### 1. Overview

Purpose: entry point, current engine readiness and recent user activity.

Must include:

- clear `New Migration` CTA
- engine status from `GET /api/v1/engine/status`
- backend health indicator
- recent migration cards only when real migration IDs are available in the current browser session or returned by the backend
- no fabricated organization-wide statistics

### 2. New Migration

Create a high-quality drag-and-drop upload experience.

Show:

- accepted extensions
- selected filename
- file size
- remove/replace action
- `Analyze` primary action
- `Analyze & Migrate` secondary/alternate action only if it maps cleanly to the current APIs

Validate extension client-side, but still respect backend validation.

### 3. Assessment

Render the actual analysis response from `POST /api/v1/analyze`.

Use clear sections for:

- workbook/source metadata
- source object counts available in the response
- dimension-level coverage scores
- overall mechanical migration coverage
- explicit review items

Important wording:

- use `Mechanical Migration Coverage` or `Migration Coverage`
- never label this as `Visual Fidelity`
- never imply a percentage is guaranteed conversion accuracy

Visualize coverage using compact progress bars or horizontal meters. Avoid radial gauges unless they materially improve readability.

### 4. Migration Plan

Present a split between:

- deterministic / automatically handled constructs
- review-required constructs

If the current response does not provide a direct auto-count, derive only when mathematically safe from explicit response fields. Otherwise show the review queue and available coverage dimensions without inventing counts.

### 5. Migration Execution / Status

Call `POST /api/v1/migrate` using the uploaded file.

The current API is request/response rather than a live event stream. Therefore do not fake step-by-step progress. Show honest states such as:

- Uploading
- Running deterministic migration
- Validating generated artifacts
- Completed / Review Required / Failed

When the API completes, render its returned status.

### 6. Migration Results

Must show:

- migration ID
- final status
- mechanical coverage
- engine availability/status
- validation result
- review-required items
- artifact/download action

Render validation checks individually when present.

### 7. Review / Remediation

For the first frontend version this can be read-only because edit/approve APIs do not exist yet.

For each review item show, if available:

- category/type
- severity
- construct name
- reason
- source formula/details

Do not display buttons such as `Approve`, `AI Fix`, `Revalidate`, or `Edit DAX` unless corresponding backend APIs exist.

### 8. Engine / System Status

Use `/health` and `/api/v1/engine/status`.

Show:

- API online/offline
- migration engine available/unavailable
- pinned commit if provided
- useful setup guidance when unavailable

Do not expose raw local filesystem paths as a prominent user-facing value.

## State management

Keep it simple:

- React state/context or a small query/state layer
- store current migration ID and recent IDs in browser storage for convenience
- backend remains authoritative
- no fake seed data in production views

## API error handling

Provide useful product states for:

- unsupported file type
- empty upload
- engine unavailable
- migration failure
- validation failure/warning
- network/backend unavailable

Avoid raw stack traces in the UI.

## Frontend folder structure

Use a maintainable structure similar to:

```text
frontend/
├── src/
│   ├── api/
│   ├── components/
│   ├── layouts/
│   ├── pages/
│   ├── types/
│   ├── hooks/
│   ├── utils/
│   ├── App.tsx
│   └── main.tsx
├── public/
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
└── README.md
```

## Backend safety boundary

Do not modify or replace these unless a concrete frontend integration issue requires it:

- `tab2pbi/parser.py`
- `tab2pbi/assessment.py`
- `tab2pbi/engine.py`
- `tab2pbi/engine_runner.py`
- `tab2pbi/orchestrator.py`
- `scripts/vendor_engine.py`
- `vendor/ENGINE_LOCK.json`

Do not add Guust, RAS, Copilot CLI, MCP, or other migration wrappers.

## Definition of done

Before considering the frontend complete:

1. `npm install` succeeds.
2. `npm run build` succeeds.
3. `npm run lint` succeeds if linting is configured.
4. Frontend runs locally and calls the existing FastAPI backend.
5. Upload/analyze works with `.twb` and `.twbx` flows.
6. Migrate calls the real backend endpoint.
7. Assessment numbers come only from API responses.
8. Engine-unavailable state is handled correctly.
9. Failed requests show clear recovery messaging.
10. No fake migration statistics or hardcoded assessment results remain.
11. Do not commit `node_modules`, build output, secrets or local environment files.

## Important product rule

The frontend is a presentation and workflow layer. Do not reimplement Tableau parsing, DAX translation, TMDL/PBIR generation or migration scoring in JavaScript. Those remain backend responsibilities.
