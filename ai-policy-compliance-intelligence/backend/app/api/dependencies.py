from app.services.analytics_service import AnalyticsService
from app.services.compliance_service import ComplianceService
from app.services.ingestion_service import IngestionService
from app.services.retrieval_service import RetrievalService


def get_ingestion_service() -> IngestionService:
    return IngestionService()


def get_retrieval_service() -> RetrievalService:
    return RetrievalService()


def get_compliance_service() -> ComplianceService:
    return ComplianceService()


def get_analytics_service() -> AnalyticsService:
    return AnalyticsService()
