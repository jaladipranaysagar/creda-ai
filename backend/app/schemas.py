from datetime import datetime

from pydantic import BaseModel, Field


class ScanRequest(BaseModel):
    content: str = Field(min_length=1, max_length=10_000, description="Message, URL, or online content to inspect")


class Finding(BaseModel):
    label: str
    detail: str
    points: int


class ScanResult(BaseModel):
    id: int
    score: int
    risk_level: str
    category: str
    summary: str
    findings: list[Finding]
    created_at: datetime


class HistoryItem(BaseModel):
    id: int
    content: str
    score: int
    risk_level: str
    category: str
    created_at: datetime

