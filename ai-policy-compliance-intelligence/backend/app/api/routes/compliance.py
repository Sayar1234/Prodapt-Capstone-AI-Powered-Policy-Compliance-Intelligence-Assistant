from fastapi import APIRouter, Depends

from app.api.dependencies import get_analytics_service, get_compliance_service, get_retrieval_service
from app.models.request_models import ComplianceCheckRequest, SearchRequest
from app.models.response_models import AnalyticsResponse, ComplianceCheckResponse, SearchResponse
from app.services.analytics_service import AnalyticsService
from app.services.compliance_service import ComplianceService
from app.services.retrieval_service import RetrievalService

router = APIRouter(prefix="/compliance", tags=["compliance"])


@router.post("/check", response_model=ComplianceCheckResponse)
async def check_compliance(request: ComplianceCheckRequest, service: ComplianceService = Depends(get_compliance_service)) -> ComplianceCheckResponse:
    return await service.check(request)


@router.post("/search", response_model=SearchResponse)
async def search_policies(request: SearchRequest, service: RetrievalService = Depends(get_retrieval_service)) -> SearchResponse:
    return SearchResponse(query=request.query, results=service.search(request.query, request.top_k, request.policy_type))


@router.get("/analytics", response_model=AnalyticsResponse)
async def analytics(service: AnalyticsService = Depends(get_analytics_service)) -> AnalyticsResponse:
    return service.summary()
