from fastapi.testclient import TestClient

from app.api import airports, routes
from app.main import app


class StubService:
    def search_airports(self, query: str):
        return {
            "query": query,
            "results": [
                {
                    "iata": "JFK",
                    "airport_name": "John F Kennedy Intl",
                    "city": "New York",
                    "state": "NY",
                    "country": "US",
                }
            ],
            "metadata": {
                "data_source": "postgres",
                "is_fallback": False,
                "data_complete": True,
                "note": None,
            },
        }

    def explore_routes(self, origin: str):
        return {
            "origin": origin,
            "routes": [],
            "metadata": {
                "data_source": "postgres",
                "is_fallback": False,
                "data_complete": True,
                "note": None,
            },
        }

    def route_detail(self, origin: str, destination: str):
        return {
            "route_summary": {
                "origin": {
                    "iata": origin,
                    "airport_name": "Origin Airport",
                    "city": "Origin City",
                    "state": "OS",
                    "country": "US",
                },
                "destination": {
                    "iata": destination,
                    "airport_name": "Destination Airport",
                    "city": "Dest City",
                    "state": "DS",
                    "country": "US",
                },
            },
            "monthly_fare_trend": [],
            "reliability_trend": [],
            "latest_score_breakdown": None,
            "cheapest_month": None,
            "methodology_hint": "hint",
            "metadata": {
                "data_source": "postgres",
                "is_fallback": False,
                "data_complete": True,
                "note": None,
            },
        }

    def airport_context(self, iata: str):
        return {
            "airport": {
                "iata": iata,
                "airport_name": "John F Kennedy Intl",
                "city": "New York",
                "state": "NY",
                "country": "US",
            },
            "latest_enplanement": None,
            "related_routes": [],
            "metadata": {
                "data_source": "postgres",
                "is_fallback": False,
                "data_complete": True,
                "note": None,
            },
        }


def test_methodology_endpoint_shape() -> None:
    client = TestClient(app)
    response = client.get("/meta/methodology")
    assert response.status_code == 200
    body = response.json()
    assert body["score_version"] == "v1_heuristic"
    assert "metric_descriptions" in body


def test_airports_and_routes_endpoints_with_stubbed_services() -> None:
    stub = StubService()
    airports.service = stub
    routes.service = stub

    client = TestClient(app)

    search_resp = client.get("/airports/search?q=jfk")
    assert search_resp.status_code == 200
    assert search_resp.json()["results"][0]["iata"] == "JFK"

    explore_resp = client.get("/routes/explore?origin=jfk")
    assert explore_resp.status_code == 200
    assert explore_resp.json()["origin"] == "JFK"

    detail_resp = client.get("/routes/JFK/LAX")
    assert detail_resp.status_code == 200
    assert detail_resp.json()["route_summary"]["destination"]["iata"] == "LAX"

    context_resp = client.get("/airports/JFK/context")
    assert context_resp.status_code == 200
    assert context_resp.json()["airport"]["iata"] == "JFK"
