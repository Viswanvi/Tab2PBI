from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path


def load_engine(engine_root: Path):
    scripts = engine_root / "skills" / "tableau-migration" / "scripts"
    module_path = scripts / "migrate_estate.py"
    if not module_path.exists():
        raise FileNotFoundError(module_path)
    sys.path.insert(0, str(scripts))
    spec = importlib.util.spec_from_file_location("tab2pbi_upstream_migrate_estate", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load upstream migration engine")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--engine-root", required=True)
    parser.add_argument("--input-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    module = load_engine(Path(args.engine_root))
    source = module.LocalFilesSource(str(Path(args.input_dir)))
    report = module.migrate_estate(source, str(Path(args.output_dir)), pbip=True)
    print(json.dumps({"status": "completed", "report_status": report.get("status") if isinstance(report, dict) else None}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
