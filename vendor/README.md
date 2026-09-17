# Vendored migration engine

The deterministic Power BI artifact generator is deliberately isolated behind `tab2pbi.engine.TableauFabricSkillsEngine`.

Run:

```bash
python scripts/vendor_engine.py
```

This checks out the exact revision in `ENGINE_LOCK.json`. Requests never download code from GitHub; production images should vendor the engine during build/deployment and then run offline.

The adapter invokes the upstream Python API (`LocalFilesSource` + `migrate_estate`) through `tab2pbi.engine_runner`, avoiding Guust/Copilot CLI/plugin requirements and avoiding the RAS PowerShell wrapper.
