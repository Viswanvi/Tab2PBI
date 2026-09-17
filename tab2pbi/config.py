from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    workspace: Path
    engine_root: Path
    engine_timeout_seconds: int


def get_settings() -> Settings:
    workspace = Path(os.getenv("TAB2PBI_WORKSPACE", "workspace")).resolve()
    engine_root = Path(os.getenv("TAB2PBI_ENGINE_ROOT", "vendor/tableau-fabric-skills")).resolve()
    timeout = int(os.getenv("TAB2PBI_ENGINE_TIMEOUT_SECONDS", "1800"))
    workspace.mkdir(parents=True, exist_ok=True)
    return Settings(workspace=workspace, engine_root=engine_root, engine_timeout_seconds=timeout)
