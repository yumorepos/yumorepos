from fastapi import APIRouter

from app.schemas.meta import MethodologyResponse
from app.services.analytics import AnalyticsService

router = APIRouter(prefix="/meta", tags=["meta"])
service = AnalyticsService()


@router.get("/methodology", response_model=MethodologyResponse)
def methodology() -> MethodologyResponse:
    return service.methodology()
