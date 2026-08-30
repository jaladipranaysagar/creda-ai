import json
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import Scan
from .schemas import Finding, HistoryItem, ScanRequest, ScanResult
from .services.analyzer import analyze

FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Creda AI", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/scans", response_model=ScanResult, status_code=201)
def create_scan(payload: ScanRequest, db: Session = Depends(get_db)):
    score, risk_level, category, findings = analyze(payload.content)
    record = Scan(
        content=payload.content.strip(), score=score, risk_level=risk_level,
        category=category, reasons=json.dumps([finding.__dict__ for finding in findings]),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    summary = "No strong risk signals were found." if not findings else f"Found {len(findings)} explainable risk signal{'s' if len(findings) != 1 else ''}."
    return ScanResult(id=record.id, score=score, risk_level=risk_level, category=category, summary=summary, findings=[Finding(**f.__dict__) for f in findings], created_at=record.created_at)


@app.get("/api/scans", response_model=list[HistoryItem])
def list_scans(limit: int = 10, db: Session = Depends(get_db)):
    safe_limit = min(max(limit, 1), 50)
    records = db.scalars(select(Scan).order_by(Scan.created_at.desc()).limit(safe_limit)).all()
    return [HistoryItem(id=row.id, content=row.content, score=row.score, risk_level=row.risk_level, category=row.category, created_at=row.created_at) for row in records]


@app.get("/")
def dashboard():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/{asset_path:path}")
def static_assets(asset_path: str):
    file_path = (FRONTEND_DIR / asset_path).resolve()
    if FRONTEND_DIR not in file_path.parents or not file_path.is_file():
        raise HTTPException(status_code=404, detail="Not found")
    return FileResponse(file_path)

