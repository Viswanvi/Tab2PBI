from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "vendor" / "ENGINE_LOCK.json"
TARGET = ROOT / "vendor" / "tableau-fabric-skills"

# Deliberately allow only the direct engine source we audited. This prevents a
# future lock-file edit from silently substituting a wrapper/fork from another
# migration toolkit.
ALLOWED_REPOSITORY = "https://github.com/Yarbrdab000/tableau-fabric-skills.git"
ALLOWED_OWNER = "Yarbrdab000"
ALLOWED_COMPONENT = "skills/tableau-migration"
ALLOWED_LICENSE = "MIT"


def run(*args: str) -> None:
    subprocess.run(args, cwd=ROOT, check=True)


def output(*args: str) -> str:
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()


def validate_lock(spec: dict) -> None:
    expected = {
        "repository": ALLOWED_REPOSITORY,
        "source_owner": ALLOWED_OWNER,
        "component": ALLOWED_COMPONENT,
        "license": ALLOWED_LICENSE,
        "provenance_statement": "CLEANROOM.md",
        "allowed_runtime_origin": True,
    }
    for key, value in expected.items():
        if spec.get(key) != value:
            raise RuntimeError(
                f"Engine provenance lock rejected: {key}={spec.get(key)!r}; expected {value!r}"
            )
    commit = str(spec.get("commit", ""))
    if len(commit) != 40 or any(ch not in "0123456789abcdef" for ch in commit.lower()):
        raise RuntimeError("Engine provenance lock must pin a full 40-character Git commit SHA")


def verify_checkout(spec: dict) -> None:
    commit = spec["commit"]
    actual_commit = output("git", "-C", str(TARGET), "rev-parse", "HEAD")
    if actual_commit != commit:
        raise RuntimeError(f"Vendored engine commit mismatch: {actual_commit} != {commit}")

    remote = output("git", "-C", str(TARGET), "remote", "get-url", "origin")
    if remote.rstrip("/") != ALLOWED_REPOSITORY.rstrip("/"):
        raise RuntimeError(f"Vendored engine origin mismatch: {remote}")

    component = TARGET / spec["component"]
    if not component.is_dir():
        raise RuntimeError(f"Pinned engine component missing: {component}")

    provenance = TARGET / spec["provenance_statement"]
    if not provenance.is_file():
        raise RuntimeError("Pinned upstream is missing its clean-room provenance statement")
    text = provenance.read_text(encoding="utf-8", errors="replace")
    required_phrases = ("original work", "No third-party", "tableau-migration")
    missing = [phrase for phrase in required_phrases if phrase.lower() not in text.lower()]
    if missing:
        raise RuntimeError(f"Upstream provenance statement missing expected assertions: {missing}")


def main() -> int:
    spec = json.loads(LOCK.read_text(encoding="utf-8"))
    validate_lock(spec)
    repo = spec["repository"]
    commit = spec["commit"]

    if TARGET.exists():
        try:
            verify_checkout(spec)
            print(f"Engine already pinned and provenance-verified at {commit}")
            return 0
        except Exception:
            shutil.rmtree(TARGET)

    TARGET.parent.mkdir(parents=True, exist_ok=True)
    run("git", "clone", "--no-tags", repo, str(TARGET))
    run("git", "-C", str(TARGET), "checkout", "--detach", commit)
    verify_checkout(spec)
    print(f"Vendored and provenance-verified {spec['name']} at {commit}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
