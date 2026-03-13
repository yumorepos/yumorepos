from fastapi import HTTPException

from app.core.config import settings
from app.core.db import DatabaseUnavailableError
from app.repositories.analytics import AnalyticsRepository
from app.schemas.airport import (
    AirportContextAirport,
    AirportContextResponse,
    AirportEnplanementContext,
    AirportSearchResponse,
    AirportSearchResult,
    RelatedRouteContext,
)
from app.schemas.common import DataProvenance
from app.schemas.meta import MethodologyResponse
from app.schemas.route import (
    CheapestMonth,
    MonthlyFarePoint,
    ReliabilityPoint,
    ReliabilitySummary,
    RouteDetailResponse,
    RouteExploreCard,
    RouteExploreResponse,
    RouteSummary,
    ScoreBreakdown,
)


class AnalyticsService:
    def __init__(self, repository: AnalyticsRepository | None = None) -> None:
        self.repository = repository or AnalyticsRepository()

    def _metadata(self) -> DataProvenance:
        if settings.use_csv_fallback:
            return DataProvenance(
                data_source="local_marts_csv",
                is_fallback=True,
                data_complete=False,
                note="CSV fallback mode is enabled; airport names/city/state and reliability coverage may be incomplete.",
            )
        return DataProvenance()

    def search_airports(self, query: str) -> AirportSearchResponse:
        try:
            rows = self.repository.search_airports(query=query)
        except DatabaseUnavailableError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

        results = [AirportSearchResult(**row) for row in rows]
        return AirportSearchResponse(
            query=query,
            results=results,
            metadata=self._metadata(),
        )

    def explore_routes(self, origin: str) -> RouteExploreResponse:
        try:
            rows = self.repository.get_route_explorer(origin_iata=origin)
        except DatabaseUnavailableError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

        cards: list[RouteExploreCard] = []
        for row in rows:
            headline_fare_insight = (
                f"Latest observed average fare: ${row['latest_avg_fare_usd']:.0f}" if row["latest_avg_fare_usd"] is not None else None
            )
            cards.append(
                RouteExploreCard(
                    destination=AirportContextAirport(
                        iata=row["destination_iata"],
                        airport_name=row["destination_airport_name"],
                        city=row["destination_city"],
                        state=row["destination_state"],
                        country=row["destination_country"],
                    ),
                    latest_route_attractiveness_score=row["latest_route_attractiveness_score"],
                    latest_deal_signal=row["deal_signal"],
                    headline_fare_insight=headline_fare_insight,
                    reliability_summary=ReliabilitySummary(
                        avg_ontime_rate=row["avg_ontime_rate"],
                        avg_cancellation_rate=row["avg_cancellation_rate"],
                    ),
                    score_confidence=row["score_confidence"],
                )
            )

        return RouteExploreResponse(origin=origin, routes=cards, metadata=self._metadata())

    def route_detail(self, origin: str, destination: str) -> RouteDetailResponse:
        try:
            payload = self.repository.get_route_detail(origin_iata=origin, destination_iata=destination)
        except DatabaseUnavailableError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

        if payload is None:
            raise HTTPException(status_code=404, detail="Route not found.")

        route = payload["route"]
        return RouteDetailResponse(
            route_summary=RouteSummary(
                origin=AirportContextAirport(
                    iata=route["origin_iata"],
                    airport_name=route["origin_airport_name"],
                    city=route["origin_city"],
                    state=route["origin_state"],
                    country=route["origin_country"],
                ),
                destination=AirportContextAirport(
                    iata=route["destination_iata"],
                    airport_name=route["destination_airport_name"],
                    city=route["destination_city"],
                    state=route["destination_state"],
                    country=route["destination_country"],
                ),
            ),
            monthly_fare_trend=[MonthlyFarePoint(**point) for point in payload["fares"]],
            reliability_trend=[ReliabilityPoint(**point) for point in payload["reliability"]],
            latest_score_breakdown=ScoreBreakdown(**payload["score"]) if payload["score"] else None,
            cheapest_month=CheapestMonth(**payload["cheapest_month"]) if payload["cheapest_month"] else None,
            methodology_hint="Scores are generated via v1_heuristic methodology; consult /meta/methodology for caveats.",
            metadata=self._metadata(),
        )

    def airport_context(self, iata: str) -> AirportContextResponse:
        try:
            payload = self.repository.get_airport_context(iata=iata)
        except DatabaseUnavailableError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

        if payload is None:
            raise HTTPException(status_code=404, detail="Airport not found.")

        airport = payload["airport"]
        return AirportContextResponse(
            airport=AirportContextAirport(
                iata=airport["iata"],
                airport_name=airport["airport_name"],
                city=airport["city"],
                state=airport["state"],
                country=airport["country"],
            ),
            latest_enplanement=AirportEnplanementContext(**payload["enplanement"]) if payload["enplanement"] else None,
            related_routes=[RelatedRouteContext(**route) for route in payload["related_routes"]],
            metadata=self._metadata(),
        )

    def methodology(self) -> MethodologyResponse:
        return MethodologyResponse(
            score_version="v1_heuristic",
            metric_descriptions={
                "reliability_score": "Scaled 0-100 from route-level on-time and cancellation behavior.",
                "fare_volatility": "Relative variability in observed route fares across available months.",
                "route_attractiveness_score": "Composite score blending fare and reliability indicators.",
                "deal_signal": "Categorical signal: strong_deal, deal, neutral, or expensive.",
            },
            caveats=[
                "Coverage is limited to loaded BTS and FAA slices in the local mart dataset.",
                "Scores are heuristic and intended for MVP decision support, not financial-grade forecasting.",
                "Sparse routes may have low confidence due to limited monthly observations.",
            ],
            source_coverage_notes=[
                "Fares: BTS DB1B-derived monthly aggregates.",
                "Reliability: BTS On-Time Performance-derived on-time and cancellation marts.",
                "Airport context: FAA annual enplanements when available.",
            ],
        )
