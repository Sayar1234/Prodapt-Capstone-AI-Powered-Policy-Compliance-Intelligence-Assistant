from app.agents.orchestrator import ComplianceOrchestrator
from app.models.request_models import ComplianceCheckRequest
from app.models.response_models import ComplianceCheckResponse


class ComplianceService:
    def __init__(self) -> None:
        self.orchestrator = ComplianceOrchestrator()

    async def check(self, request: ComplianceCheckRequest) -> ComplianceCheckResponse:
        return await self.orchestrator.check(
            query=request.query,
            top_k=request.top_k,
            policy_type=request.policy_type,
            include_recommendations=request.include_recommendations,
        )
