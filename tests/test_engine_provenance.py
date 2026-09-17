import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "vendor" / "ENGINE_LOCK.json"


def test_engine_lock_points_only_to_audited_direct_source():
    spec = json.loads(LOCK.read_text(encoding="utf-8"))
    assert spec["repository"] == "https://github.com/Yarbrdab000/tableau-fabric-skills.git"
    assert spec["source_owner"] == "Yarbrdab000"
    assert spec["component"] == "skills/tableau-migration"
    assert spec["license"] == "MIT"
    assert spec["provenance_statement"] == "CLEANROOM.md"
    assert spec["allowed_runtime_origin"] is True
    commit = spec["commit"]
    assert len(commit) == 40
    int(commit, 16)


def test_repo_does_not_declare_guust_or_ras_as_runtime_sources():
    runtime_files = [
        ROOT / "requirements.txt",
        ROOT / "pyproject.toml",
        ROOT / "tab2pbi" / "engine.py",
        ROOT / "tab2pbi" / "engine_runner.py",
        ROOT / "Dockerfile",
    ]
    banned = ("guust", "rasgiza", "tableau-migration-accelerator")
    for path in runtime_files:
        text = path.read_text(encoding="utf-8").lower()
        assert not any(term in text for term in banned), f"Unexpected runtime source reference in {path}"
