from fastapi import APIRouter, Query

from app.schemas.airport import AirportContextResponse, AirportSearchResponse
from app.services.analytics import AnalyticsService

router = APIRouter(prefix="/airports", tags=["airports"])
service = AnalyticsService()


@router.get("/search", response_model=AirportSearchResponse)
def airport_search(q: str = Query(min_length=1, max_length=60)) -> AirportSearchResponse:
    return service.search_airports(query=q.strip().upper())


@router.get("/{iata}/context", response_model=AirportContextResponse)
def airport_context(iata: str) -> AirportContextResponse:
    return service.airport_context(iata=iata.strip().upper())
