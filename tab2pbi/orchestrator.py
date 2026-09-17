from __future__ import annotations

import json
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path

from .assessment import assess
from .config import Settings
from .engine import EngineExecutionError, EngineUnavailable, TableauFabricSkillsEngine
from .models import AnalysisResponse, MigrationResponse
from .parser import parse_tableau
from .validation import validate_output


class MigrationOrchestrator:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.engine = TableauFabricSkillsEngine(settings)

    def _job_dir(self, migration_id: str) -> Path:
        return self.settings.workspace / "jobs" / migration_id

    def stage(self, filename: str, data: bytes, migration_id: str | None = None) -> tuple[str, Path, Path]:
        migration_id = migration_id or uuid.uuid4().hex
        job = self._job_dir(migration_id)
        input_dir = job / "input"
        output_dir = job / "output"
        input_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        safe_name = Path(filename or "upload.twbx").name
        source_path = input_dir / safe_name
        source_path.write_bytes(data)
        return migration_id, source_path, output_dir

    def analyze_path(self, source_path: Path, migration_id: str) -> AnalysisResponse:
        ir = parse_tableau(source_path)
        result = AnalysisResponse(migration_id=migration_id, ir=ir, assessment=assess(ir))
        meta = self._job_dir(migration_id) / "analysis.json"
        meta.write_text(result.model_dump_json(indent=2), encoding="utf-8")
        return result

    def migrate_path(self, source_path: Path, migration_id: str, output_dir: Path) -> MigrationResponse:
        analysis = self.analyze_path(source_path, migration_id)
        engine_status = self.engine.status()
        created = datetime.now(timezone.utc)
        if not engine_status.available:
            response = MigrationResponse(
                migration_id=migration_id, status="review", analysis=analysis, engine=engine_status,
                created_at=created,
                artifacts={"analysis": str(self._job_dir(migration_id) / "analysis.json")},
            )
            self._persist_result(response)
            return response

        try:
            report = self.engine.migrate(source_path.parent, output_dir)
            validation = validate_output(output_dir)
            status = "failed" if validation.status == "fail" else "review" if (validation.status == "warn" or analysis.assessment.review_items) else "completed"
            response = MigrationResponse(
                migration_id=migration_id,
                status=status,
                analysis=analysis,
                engine=engine_status,
                validation=validation,
                engine_report=report,
                created_at=created,
                artifacts={"output_dir": str(output_dir)},
            )
        except (EngineUnavailable, EngineExecutionError, TimeoutError) as exc:
            response = MigrationResponse(
                migration_id=migration_id, status="failed", analysis=analysis, engine=engine_status,
                created_at=created,
                artifacts={"error": str(exc)},
            )
        self._persist_result(response)
        return response

    def _persist_result(self, response: MigrationResponse) -> None:
        path = self._job_dir(response.migration_id) / "result.json"
        path.write_text(response.model_dump_json(indent=2), encoding="utf-8")

    def load_result(self, migration_id: str) -> dict:
        path = self._job_dir(migration_id) / "result.json"
        if not path.exists():
            analysis = self._job_dir(migration_id) / "analysis.json"
            if analysis.exists():
                return {"migration_id": migration_id, "status": "analysed", "analysis": json.loads(analysis.read_text(encoding="utf-8"))}
            raise FileNotFoundError(migration_id)
        return json.loads(path.read_text(encoding="utf-8"))

    def make_bundle(self, migration_id: str) -> Path:
        job = self._job_dir(migration_id)
        if not job.exists():
            raise FileNotFoundError(migration_id)
        archive_base = job / f"tab2pbi-{migration_id}"
        return Path(shutil.make_archive(str(archive_base), "zip", root_dir=job))
