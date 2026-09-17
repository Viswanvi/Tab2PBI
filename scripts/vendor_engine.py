from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "vendor" / "ENGINE_LOCK.json"
TARGET = ROOT / "vendor" / "tableau-fabric-skills"


def run(*args: str) -> None:
    subprocess.run(args, cwd=ROOT, check=True)


def main() -> int:
    spec = json.loads(LOCK.read_text(encoding="utf-8"))
    repo = spec["repository"]
    commit = spec["commit"]

    if TARGET.exists():
        current = subprocess.run(
            ["git", "-C", str(TARGET), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
        )
        if current.returncode == 0 and current.stdout.strip() == commit:
            print(f"Engine already pinned at {commit}")
            return 0
        shutil.rmtree(TARGET)

    TARGET.parent.mkdir(parents=True, exist_ok=True)
    run("git", "clone", "--no-tags", repo, str(TARGET))
    run("git", "-C", str(TARGET), "checkout", "--detach", commit)
    print(f"Vendored {spec['name']} at {commit}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
