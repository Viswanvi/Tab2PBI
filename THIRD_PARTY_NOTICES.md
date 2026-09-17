# Third-party notices

Tab2PBI's own orchestration code is separate from the optional migration engine.

## tableau-fabric-skills

- Upstream: https://github.com/Yarbrdab000/tableau-fabric-skills
- Component used: `skills/tableau-migration`
- License reported by upstream: MIT
- Pinned revision: see `vendor/ENGINE_LOCK.json`

`python scripts/vendor_engine.py` checks out the exact pinned upstream revision into `vendor/tableau-fabric-skills/`. The upstream `LICENSE`, `THIRD_PARTY_NOTICES.md` and source history remain intact in that checkout.

## Guust Tableau → Power BI migration project

- Upstream: https://github.com/Guust-Franssens/tableau-to-powerbi-migration
- Used as an architectural reference for parsing/validation/remediation concepts.
- Tab2PBI does not require Guust's Copilot CLI agents or plugin runtime.

## RAS Tableau Migration Accelerator

- Upstream: https://github.com/rasgiza/tableau-migration-accelerator
- Used as an architectural reference for deterministic conversion and human-review gates.
- Tab2PBI does not execute the RAS PowerShell wrapper.
