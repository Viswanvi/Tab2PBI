# Tab2PBI Frontend Workspace

This folder is reserved for the production frontend of Tab2PBI.

## Recommended stack

- React 18+
- TypeScript
- Vite
- Tailwind CSS
- React Router
- Native `fetch` or a very small API client wrapper

Do not move or duplicate the Tableau → Power BI migration engine into the frontend. The frontend must communicate only with the FastAPI backend.

## Backend during local development

From the repository root:

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
pip install -r requirements.txt
python scripts/vendor_engine.py
uvicorn tab2pbi.main:app --reload --port 8000
```

Backend URL: `http://127.0.0.1:8000`

## Existing API contract

- `GET /health`
- `GET /api/v1/engine/status`
- `POST /api/v1/analyze` — multipart upload field name: `file`
- `POST /api/v1/migrate` — multipart upload field name: `file`
- `GET /api/v1/jobs/{migration_id}`
- `GET /api/v1/jobs/{migration_id}/download`

Accepted uploads: `.twb`, `.twbx`, `.tds`, `.tdsx`.

## Rules for the frontend implementation

1. Do not change migration-engine code under `tab2pbi/engine.py`, `tab2pbi/engine_runner.py`, `scripts/vendor_engine.py`, or `vendor/` unless explicitly required.
2. Do not introduce Guust, RAS, Copilot CLI, MCP, or agent runtime dependencies.
3. Never hardcode assessment results, migration percentages, workbook counts, or validation outcomes.
4. Every number/status shown must come from the FastAPI response or be clearly marked unavailable.
5. Do not represent mechanical migration coverage as visual fidelity.
6. Keep unsupported/review-required constructs visible to the user.
7. Do not expose filesystem paths from backend responses directly in normal UI.
8. Treat failed API requests as product states with useful recovery actions, not generic alerts.

See `docs/ANTIGRAVITY_FRONTEND_BRIEF.md` for the complete frontend build brief.
