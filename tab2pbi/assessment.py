from __future__ import annotations

import re

from .models import Assessment, DimensionScore, MigrationIR, ReviewItem

SUPPORTED_MARKS = {
    "automatic", "bar", "line", "area", "circle", "square", "text", "shape", "pie", "map"
}
HARD_CALC_PATTERNS = {
    "table_calc": re.compile(r"\b(WINDOW_|LOOKUP\s*\(|INDEX\s*\(|PREVIOUS_VALUE\s*\(|RUNNING_|TOTAL\s*\()", re.I),
    "lod_include_exclude": re.compile(r"\{\s*(INCLUDE|EXCLUDE)\b", re.I),
    "nested_lod": re.compile(r"\{[^{}]*\{", re.S),
}


def _score(total: int, review: int) -> int:
    if total <= 0:
        return 100
    return max(0, min(100, round(100 * (total - review) / total)))


def assess(ir: MigrationIR) -> Assessment:
    issues: list[ReviewItem] = []

    calc_review = 0
    for ds in ir.datasources:
        for field in ds.fields:
            if not field.formula:
                continue
            matched = None
            for code, pattern in HARD_CALC_PATTERNS.items():
                if pattern.search(field.formula):
                    matched = code
                    break
            if matched:
                calc_review += 1
                issues.append(ReviewItem(
                    code=f"calc.{matched}", category="calculation", severity="high" if matched == "nested_lod" else "medium",
                    object_name=field.caption or field.name,
                    message="Calculation requires semantic review; do not silently translate it as ordinary row/filter context DAX.",
                ))

    visual_total = max(1, len(ir.worksheets))
    visual_review = 0
    for ws in ir.worksheets:
        marks = ws.mark_classes or ["Automatic"]
        unsupported = [m for m in marks if m.lower() not in SUPPORTED_MARKS]
        if unsupported:
            visual_review += 1
            issues.append(ReviewItem(
                code="visual.unsupported_mark", category="visual", severity="medium", object_name=ws.name,
                message=f"Worksheet uses mark class(es) requiring review: {', '.join(unsupported)}.",
            ))

    action_review = ir.actions
    if ir.actions:
        issues.append(ReviewItem(
            code="interaction.dashboard_action", category="interaction", severity="medium",
            message=f"{ir.actions} Tableau action(s) detected; dashboard interactions require explicit Power BI mapping/validation.",
        ))

    relationship_review = 0
    if ir.relationships and len(ir.datasources) > 1:
        relationship_review = max(1, ir.relationships // 4)
        issues.append(ReviewItem(
            code="model.relationship_review", category="relationship", severity="medium",
            message="Relationships were detected across a multi-datasource workbook; cardinality/filter direction must be validated.",
        ))

    dims = [
        DimensionScore(name="schema", score=100, automated=ir.raw_counts.get("fields", 0), review=0, total=ir.raw_counts.get("fields", 0)),
        DimensionScore(name="calculations", score=_score(ir.calculations, calc_review), automated=max(0, ir.calculations-calc_review), review=calc_review, total=ir.calculations),
        DimensionScore(name="visual_structure", score=_score(visual_total, visual_review), automated=max(0, visual_total-visual_review), review=visual_review, total=visual_total),
        DimensionScore(name="filters_parameters", score=90 if ir.parameters else 100, automated=sum(w.filters for w in ir.worksheets), review=ir.parameters, total=sum(w.filters for w in ir.worksheets)+ir.parameters),
        DimensionScore(name="relationships", score=_score(ir.relationships, relationship_review), automated=max(0, ir.relationships-relationship_review), review=relationship_review, total=ir.relationships),
        DimensionScore(name="interactions", score=_score(max(1, ir.actions), action_review), automated=0 if ir.actions else 1, review=action_review, total=max(1, ir.actions)),
    ]
    weights = {"schema": 15, "calculations": 25, "visual_structure": 25, "filters_parameters": 10, "relationships": 15, "interactions": 10}
    overall = round(sum(d.score * weights[d.name] for d in dims) / sum(weights.values()))
    return Assessment(overall_coverage=overall, dimensions=dims, review_items=issues)
