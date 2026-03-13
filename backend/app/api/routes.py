from fastapi import APIRouter, Query

from app.schemas.route import RouteDetailResponse, RouteExploreResponse
from app.services.analytics import AnalyticsService

router = APIRouter(prefix="/routes", tags=["routes"])
service = AnalyticsService()


@router.get("/explore", response_model=RouteExploreResponse)
def explore_routes(origin: str = Query(min_length=3, max_length=3)) -> RouteExploreResponse:
    return service.explore_routes(origin=origin.strip().upper())


@router.get("/{origin}/{destination}", response_model=RouteDetailResponse)
def route_detail(origin: str, destination: str) -> RouteDetailResponse:
    return service.route_detail(origin=origin.strip().upper(), destination=destination.strip().upper())
