from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from .config import Settings
from .models import EngineStatus


class EngineUnavailable(RuntimeError):
    pass


class EngineExecutionError(RuntimeError):
    pass


class TableauFabricSkillsEngine:
    def __init__(self, settings: Settings):
        self.settings = settings

    @property
    def entrypoint(self) -> Path:
        return self.settings.engine_root / "skills" / "tableau-migration" / "scripts" / "migrate_estate.py"

    def status(self) -> EngineStatus:
        lock_path = Path(__file__).resolve().parents[1] / "vendor" / "ENGINE_LOCK.json"
        pinned = None
        if lock_path.exists():
            try:
                pinned = json.loads(lock_path.read_text(encoding="utf-8")).get("commit")
            except Exception:
                pinned = None
        available = self.entrypoint.exists()
        return EngineStatus(
            available=available,
            engine_root=str(self.settings.engine_root),
            entrypoint=str(self.entrypoint),
            pinned_commit=pinned,
            detail="Pinned deterministic engine is available." if available else "Run `python scripts/vendor_engine.py` to install the pinned engine snapshot.",
        )

    def migrate(self, input_dir: Path, output_dir: Path) -> dict:
        if not self.entrypoint.exists():
            raise EngineUnavailable(self.status().detail)
        output_dir.mkdir(parents=True, exist_ok=True)
        runner = Path(__file__).with_name("engine_runner.py")
        cmd = [
            sys.executable,
            str(runner),
            "--engine-root", str(self.settings.engine_root),
            "--input-dir", str(input_dir),
            "--output-dir", str(output_dir),
        ]
        env = os.environ.copy()
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env=env,
            timeout=self.settings.engine_timeout_seconds,
        )
        if proc.returncode != 0:
            raise EngineExecutionError((proc.stderr or proc.stdout or "Engine failed").strip())
        report = output_dir / "report.json"
        if report.exists():
            return json.loads(report.read_text(encoding="utf-8-sig"))
        try:
            return json.loads(proc.stdout.strip().splitlines()[-1])
        except Exception:
            return {"status": "completed", "stdout": proc.stdout[-4000:]}
