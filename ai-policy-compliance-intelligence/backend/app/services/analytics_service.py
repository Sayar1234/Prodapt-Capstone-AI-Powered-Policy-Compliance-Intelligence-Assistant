from app.database.mongodb import store
from app.models.response_models import AnalyticsResponse


class AnalyticsService:
    def summary(self) -> AnalyticsResponse:
        return AnalyticsResponse(**store.stats())
