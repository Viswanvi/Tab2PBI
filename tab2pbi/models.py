from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class FieldIR(BaseModel):
    name: str
    caption: str | None = None
    datatype: str | None = None
    role: str | None = None
    field_type: str | None = None
    formula: str | None = None


class DatasourceIR(BaseModel):
    name: str
    caption: str | None = None
    connection_classes: list[str] = Field(default_factory=list)
    fields: list[FieldIR] = Field(default_factory=list)


class WorksheetIR(BaseModel):
    name: str
    mark_classes: list[str] = Field(default_factory=list)
    filters: int = 0
    has_rows_shelf: bool = False
    has_cols_shelf: bool = False


class DashboardIR(BaseModel):
    name: str
    zones: int = 0


class MigrationIR(BaseModel):
    source_name: str
    source_type: Literal["twb", "twbx", "tds", "tdsx"]
    datasources: list[DatasourceIR] = Field(default_factory=list)
    worksheets: list[WorksheetIR] = Field(default_factory=list)
    dashboards: list[DashboardIR] = Field(default_factory=list)
    parameters: int = 0
    relationships: int = 0
    actions: int = 0
    calculations: int = 0
    raw_counts: dict[str, int] = Field(default_factory=dict)


class ReviewItem(BaseModel):
    code: str
    category: str
    severity: Literal["low", "medium", "high"]
    message: str
    object_name: str | None = None


class DimensionScore(BaseModel):
    name: str
    score: int = Field(ge=0, le=100)
    automated: int = 0
    review: int = 0
    total: int = 0


class Assessment(BaseModel):
    overall_coverage: int = Field(ge=0, le=100)
    dimensions: list[DimensionScore]
    review_items: list[ReviewItem]
    disclaimer: str = (
        "Coverage estimates mechanical migration readiness; it is not a claim of pixel-perfect visual fidelity."
    )


class ValidationCheck(BaseModel):
    name: str
    status: Literal["pass", "warn", "fail"]
    detail: str


class ValidationResult(BaseModel):
    status: Literal["pass", "warn", "fail"]
    checks: list[ValidationCheck]


class AnalysisResponse(BaseModel):
    migration_id: str
    ir: MigrationIR
    assessment: Assessment


class EngineStatus(BaseModel):
    available: bool
    engine_root: str
    entrypoint: str
    pinned_commit: str | None = None
    detail: str


class MigrationResponse(BaseModel):
    migration_id: str
    status: Literal["completed", "review", "failed"]
    analysis: AnalysisResponse
    engine: EngineStatus
    validation: ValidationResult | None = None
    artifacts: dict[str, str] = Field(default_factory=dict)
    engine_report: dict[str, Any] | None = None
    created_at: datetime
