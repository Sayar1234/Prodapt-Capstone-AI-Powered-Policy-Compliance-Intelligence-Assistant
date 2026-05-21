from datetime import datetime

from pydantic import BaseModel, Field

from app.models.domain_models import Citation, ComplianceFinding, IngestionResult, RiskLevel


class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str
    timestamp: datetime
    services: dict[str, str]
    providers: dict[str, str] = Field(default_factory=dict)


class IngestionResponse(BaseModel):
    results: list[IngestionResult]
    message: str = "Documents ingested successfully"


class SearchResponse(BaseModel):
    query: str
    results: list[Citation]


class ComplianceCheckResponse(BaseModel):
    query: str
    answer: str
    risk_level: RiskLevel
    findings: list[ComplianceFinding] = Field(default_factory=list)
    citations: list[Citation] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


class AnalyticsResponse(BaseModel):
    documents: int
    chunks: int
    policy_types: dict[str, int]
