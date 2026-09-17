from pathlib import Path
from tab2pbi.config import Settings
from tab2pbi.engine import TableauFabricSkillsEngine


def test_engine_status_when_not_vendored(tmp_path: Path):
    settings = Settings(workspace=tmp_path / "work", engine_root=tmp_path / "missing", engine_timeout_seconds=10)
    status = TableauFabricSkillsEngine(settings).status()
    assert status.available is False
    assert "vendor_engine.py" in status.detail
