from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .config import get_settings
from .ingestion import UnsupportedInput
from .orchestrator import MigrationOrchestrator

app = FastAPI(title="Tab2PBI", version="0.1.0")
settings = get_settings()
orchestrator = MigrationOrchestrator(settings)
STATIC = Path(__file__).resolve().parent / "static"
app.mount("/ui", StaticFiles(directory=STATIC, html=True), name="ui")


@app.get("/")
def root():
    return FileResponse(STATIC / "index.html")


@app.get("/health")
def health():
    return {"status": "ok", "service": "Tab2PBI"}


@app.get("/api/v1/engine/status")
def engine_status():
    return orchestrator.engine.status()


async def _read_upload(file: UploadFile) -> bytes:
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in {".twb", ".twbx", ".tds", ".tdsx"}:
        raise HTTPException(status_code=415, detail="Upload a .twb, .twbx, .tds or .tdsx Tableau asset")
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")
    return data


@app.post("/api/v1/analyze")
async def analyze(file: UploadFile = File(...)):
    data = await _read_upload(file)
    migration_id, source_path, _ = orchestrator.stage(file.filename or "upload.twbx", data)
    try:
        return orchestrator.analyze_path(source_path, migration_id)
    except (ValueError, UnsupportedInput) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/v1/migrate")
async def migrate(file: UploadFile = File(...)):
    data = await _read_upload(file)
    migration_id, source_path, output_dir = orchestrator.stage(file.filename or "upload.twbx", data)
    try:
        return orchestrator.migrate_path(source_path, migration_id, output_dir)
    except (ValueError, UnsupportedInput) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/v1/jobs/{migration_id}")
def job(migration_id: str):
    try:
        return orchestrator.load_result(migration_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Migration job not found")


@app.get("/api/v1/jobs/{migration_id}/download")
def download(migration_id: str):
    try:
        archive = orchestrator.make_bundle(migration_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Migration job not found")
    return FileResponse(archive, media_type="application/zip", filename=archive.name)
