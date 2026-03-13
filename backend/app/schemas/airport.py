from pydantic import BaseModel

from app.schemas.common import DataProvenance


class AirportSearchResult(BaseModel):
    iata: str
    airport_name: str
    city: str | None = None
    state: str | None = None
    country: str


class AirportSearchResponse(BaseModel):
    query: str
    results: list[AirportSearchResult]
    metadata: DataProvenance


class AirportContextAirport(BaseModel):
    iata: str
    airport_name: str
    city: str | None = None
    state: str | None = None
    country: str


class AirportEnplanementContext(BaseModel):
    year: int
    total_enplanements: int


class RelatedRouteContext(BaseModel):
    destination_iata: str
    destination_city: str | None = None
    destination_airport_name: str
    latest_route_attractiveness_score: float | None = None
    latest_deal_signal: str | None = None


class AirportContextResponse(BaseModel):
    airport: AirportContextAirport
    latest_enplanement: AirportEnplanementContext | None = None
    related_routes: list[RelatedRouteContext]
    metadata: DataProvenance
