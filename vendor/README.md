# Audited deterministic migration engine

The Power BI artifact generator is isolated behind `tab2pbi.engine.TableauFabricSkillsEngine`.

Run:

```bash
python scripts/vendor_engine.py
```

The bootstrap accepts only the direct audited source declared in `ENGINE_LOCK.json`:

- repository: `https://github.com/Yarbrdab000/tableau-fabric-skills.git`
- component: `skills/tableau-migration`
- exact pinned commit: see `ENGINE_LOCK.json`
- upstream provenance file: `CLEANROOM.md`

The bootstrap verifies the repository origin, commit SHA, component path and provenance statement before accepting the checkout. Requests never download code from GitHub; production images vendor the engine during build/deployment and can then run offline.

The adapter invokes the engine Python API (`LocalFilesSource` + `migrate_estate`) through `tab2pbi.engine_runner`.

Tab2PBI does not fetch or execute Guust code, Guust agents/plugins, RAS code, or RAS PowerShell wrappers.
