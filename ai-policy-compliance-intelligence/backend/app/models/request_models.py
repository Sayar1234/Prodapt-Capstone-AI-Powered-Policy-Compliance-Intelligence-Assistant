from pydantic import BaseModel, Field


class TextIngestionRequest(BaseModel):
    title: str = Field(min_length=1, max_length=240)
    text: str = Field(min_length=20)
    source: str = "manual"
    policy_type: str = "general"
    metadata: dict[str, str | int | float | bool] = Field(default_factory=dict)


class ComplianceCheckRequest(BaseModel):
    query: str = Field(min_length=3, max_length=4000)
    policy_type: str | None = None
    top_k: int = Field(default=6, ge=1, le=20)
    include_recommendations: bool = True


class SearchRequest(BaseModel):
    query: str = Field(min_length=2, max_length=2000)
    policy_type: str | None = None
    top_k: int = Field(default=6, ge=1, le=30)


class RiskAssessmentRequest(BaseModel):
    scenario: str = Field(min_length=10, max_length=6000)
    policy_type: str | None = None
    top_k: int = Field(default=6, ge=1, le=20)
