from __future__ import annotations

import json
from pathlib import Path

from .models import ValidationCheck, ValidationResult


def validate_output(output_dir: Path) -> ValidationResult:
    checks: list[ValidationCheck] = []
    report_path = output_dir / "report.json"
    if report_path.exists():
        try:
            report = json.loads(report_path.read_text(encoding="utf-8-sig"))
            checks.append(ValidationCheck(name="engine_report", status="pass", detail="report.json is valid JSON"))
            dod = report.get("definition_of_done") if isinstance(report, dict) else None
            if dod is not None:
                checks.append(ValidationCheck(name="definition_of_done", status="pass" if str(dod).lower() not in {"fail", "failed"} else "fail", detail=f"Engine definition_of_done={dod}"))
        except Exception as exc:
            checks.append(ValidationCheck(name="engine_report", status="fail", detail=f"Invalid report.json: {exc}"))
    else:
        checks.append(ValidationCheck(name="engine_report", status="warn", detail="No report.json produced"))

    pbips = list(output_dir.rglob("*.pbip"))
    checks.append(ValidationCheck(
        name="pbip_artifact",
        status="pass" if pbips else "warn",
        detail=f"{len(pbips)} .pbip project(s) produced" if pbips else "No .pbip project found; inspect engine report/remediation items.",
    ))

    bad_json = []
    for path in output_dir.rglob("*.json"):
        try:
            json.loads(path.read_text(encoding="utf-8-sig"))
        except Exception:
            bad_json.append(str(path.relative_to(output_dir)))
    checks.append(ValidationCheck(
        name="json_integrity",
        status="pass" if not bad_json else "fail",
        detail="All generated JSON files parse." if not bad_json else f"Invalid JSON: {', '.join(bad_json[:10])}",
    ))

    statuses = {c.status for c in checks}
    overall = "fail" if "fail" in statuses else "warn" if "warn" in statuses else "pass"
    return ValidationResult(status=overall, checks=checks)
