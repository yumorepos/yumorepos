from pydantic import BaseModel

from app.schemas.airport import AirportContextAirport
from app.schemas.common import DataProvenance


class ReliabilitySummary(BaseModel):
    avg_ontime_rate: float | None = None
    avg_cancellation_rate: float | None = None


class RouteExploreCard(BaseModel):
    destination: AirportContextAirport
    latest_route_attractiveness_score: float | None = None
    latest_deal_signal: str | None = None
    headline_fare_insight: str | None = None
    reliability_summary: ReliabilitySummary
    score_confidence: float | None = None


class RouteExploreResponse(BaseModel):
    origin: str
    routes: list[RouteExploreCard]
    metadata: DataProvenance


class MonthlyFarePoint(BaseModel):
    year: int
    month: int
    avg_fare_usd: float


class ReliabilityPoint(BaseModel):
    year: int
    month: int
    ontime_rate: float | None = None
    cancellation_rate: float | None = None


class ScoreBreakdown(BaseModel):
    year: int
    month: int
    reliability_score: float | None = None
    fare_volatility: float | None = None
    route_attractiveness_score: float | None = None
    deal_signal: str


class RouteSummary(BaseModel):
    origin: AirportContextAirport
    destination: AirportContextAirport


class CheapestMonth(BaseModel):
    year: int
    month: int
    avg_fare_usd: float


class RouteDetailResponse(BaseModel):
    route_summary: RouteSummary
    monthly_fare_trend: list[MonthlyFarePoint]
    reliability_trend: list[ReliabilityPoint]
    latest_score_breakdown: ScoreBreakdown | None = None
    cheapest_month: CheapestMonth | None = None
    methodology_hint: str
    metadata: DataProvenance
