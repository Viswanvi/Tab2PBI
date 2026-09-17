# Third-party notices

Tab2PBI's orchestration, assessment, API, validation envelope, UI and job model are maintained in this repository.

## Deterministic Tableau → Power BI engine

Tab2PBI uses one pinned external migration engine:

- Upstream: https://github.com/Yarbrdab000/tableau-fabric-skills
- Source owner: `Yarbrdab000`
- Component used: `skills/tableau-migration`
- License reported by upstream: MIT
- Exact revision: see `vendor/ENGINE_LOCK.json`
- Upstream provenance statement: `CLEANROOM.md`

The pinned upstream states that `tableau-migration` is an original parser/emitter implementation based on Tableau workbook/datasource XML and Microsoft Power BI/Fabric formats, and that no third-party converter source code was copied into it. Tab2PBI verifies the direct repository origin, exact commit, component path and presence of the upstream provenance statement before accepting the vendored engine.

`python scripts/vendor_engine.py` checks out only the direct audited repository and exact pinned revision into `vendor/tableau-fabric-skills/`. The upstream source, license, notices and provenance documentation remain intact in that checkout. Requests never install or fetch Guust, RAS, Copilot plugins, or migration wrappers.

## Normal application dependencies

Tab2PBI also uses standard Python application packages such as FastAPI, Uvicorn, Pydantic and python-multipart. These provide HTTP/API/runtime functionality and do not implement Tableau → Power BI migration logic.
