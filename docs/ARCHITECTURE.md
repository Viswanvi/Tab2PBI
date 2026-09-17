# Architecture decisions

## 1. One application-owned orchestration layer

Tab2PBI does not chain Guust → RAS → tableau-fabric-skills. That would duplicate orchestration and parsing. Tab2PBI owns the request/job lifecycle and places third-party conversion behind one adapter.

## 2. Deterministic engine boundary

`TableauFabricSkillsEngine` invokes a pinned checkout of `tableau-fabric-skills/skills/tableau-migration`. `engine_runner.py` imports the upstream `LocalFilesSource` and `migrate_estate()` Python API directly. This deliberately avoids Copilot CLI, plugin registration and PowerShell as mandatory runtime dependencies.

## 3. Canonical MigrationIR

The Tab2PBI parser creates a stable IR used for assessment and future remediation. The upstream engine can continue parsing the original artifact while the MVP matures. The long-term target is to reconcile the two representations with regression fixtures before making the IR the single conversion input.

## 4. Human gates

Complex table calculations, LOD semantics, dashboard actions, unusual mark types and ambiguous relationships are review items rather than silently guessed conversions.

## 5. Validation layers

Current MVP validates engine report presence, generated JSON integrity and PBIP artifact presence. Planned layers:

1. TMDL/PBIR structural lint.
2. Microsoft `powerbi-report-author validate` where available.
3. Numeric reconciliation against Tableau exports.
4. Source-vs-target image/oracle comparison.
5. Human sign-off for remaining remediation.

## 6. AI boundary

AI remediation is intentionally an optional future layer. It may propose DAX or visual remediation, but deterministic validators and/or human approval own PASS/FAIL.
