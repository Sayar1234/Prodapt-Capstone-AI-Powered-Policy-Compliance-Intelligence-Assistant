from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class RiskLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class PolicyDocument(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    source: str
    policy_type: str = "general"
    text: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)


class DocumentChunk(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    document_id: str
    title: str
    text: str
    chunk_index: int
    policy_type: str = "general"
    source: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class Citation(BaseModel):
    document_id: str
    chunk_id: str
    title: str
    source: str
    excerpt: str
    score: float = 0.0


class ComplianceFinding(BaseModel):
    control: str
    status: str
    risk_level: RiskLevel
    evidence: list[Citation] = Field(default_factory=list)
    rationale: str
    recommendation: str


class IngestionResult(BaseModel):
    document_id: str
    title: str
    chunks_created: int
    policy_type: str
