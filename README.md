# Tab2PBI

Tab2PBI is an engineering-first Tableau → Power BI migration accelerator. It is intentionally **not** a one-click “100% conversion” claim. The platform separates deterministic conversion from assessment, validation and human remediation.

## Architecture

```text
TWB / TWBX / TDS / TDSX
          │
          ▼
   Tab2PBI ingestion
          │
          ▼
   Canonical MigrationIR
          │
     ┌────┴────┐
     ▼         ▼
 Assessment   Audited deterministic engine
     │         (direct tableau-fabric-skills source)
     │                │
     │          DAX / TMDL / PBIR / PBIP
     │                │
     └────────┬───────┘
              ▼
         Validation
              │
        ┌─────┴─────┐
        ▼           ▼
      PASS        REVIEW
                    │
             Remediation queue
```

### Provenance boundary

Tab2PBI's runtime dependency story is deliberately narrow:

- **Tab2PBI-owned:** upload/API, canonical IR, assessment, scoring, job orchestration, validation envelope, remediation model, UI and audit metadata.
- **Migration engine:** one exact pinned revision of `Yarbrdab000/tableau-fabric-skills`, component `skills/tableau-migration`.
- **No Guust runtime dependency.** Tab2PBI does not fetch, import, execute or install Guust code, agents or plugins.
- **No RAS runtime dependency.** Tab2PBI does not fetch, import, execute or install RAS code or PowerShell wrappers.
- **No Copilot/plugin requirement** for the Tab2PBI migration request path.

The vendor bootstrap validates the direct upstream repository URL, owner, exact 40-character commit SHA, component path, MIT license declaration and upstream `CLEANROOM.md` provenance statement before accepting the engine checkout.

## Quick start

Requires Python 3.11+.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install -r requirements.txt

# Run analysis-only mode immediately
uvicorn tab2pbi.main:app --reload
```

Open http://127.0.0.1:8000.

### Enable deterministic PBIP generation

The production converter is pinned and bootstrapped at build/setup time rather than downloaded at request time:

```bash
python scripts/vendor_engine.py
```

Then restart the API. `/api/v1/engine/status` should report `available: true`.

The pinned revision and provenance contract are stored in `vendor/ENGINE_LOCK.json`.

## API

- `GET /health`
- `GET /api/v1/engine/status`
- `POST /api/v1/analyze` — upload `.twb`, `.twbx`, `.tds` or `.tdsx`
- `POST /api/v1/migrate` — analyse + deterministic engine + validation; requires vendored engine
- `GET /api/v1/jobs/{job_id}` — migration metadata/result
- `GET /api/v1/jobs/{job_id}/download` — download generated migration bundle ZIP

## Migration scoring

Tab2PBI does **not** claim that a single percentage equals visual fidelity. Assessment returns separate dimensions such as calculations, visuals, filters/parameters, relationships and dashboard interactions. Unsupported constructs are surfaced as explicit review items.

## Current MVP boundary

The repository provides a working upload/analyse API and UI, deterministic assessment, job orchestration, a direct pinned adapter to the audited open-source migration engine, structural output validation and downloadable migration bundles. Fidelity image comparison and AI-assisted remediation remain extension points and are deliberately not allowed to silently approve migrations.

## Third-party code

See `THIRD_PARTY_NOTICES.md` and `vendor/README.md`. The migration engine is pinned to an exact direct-source commit and retains its upstream license/provenance files when bootstrapped.
