import csv
from pathlib import Path

from app.core.config import settings
from app.core.db import DatabaseUnavailableError


class AnalyticsRepository:
    """MVP analytics read repository.

    PostgreSQL is the intended primary source. In this environment, optional CSV fallback
    can be enabled with FPI_USE_CSV_FALLBACK=true for local marts-based responses.
    """

    def __init__(self) -> None:
        self.repo_root = Path(__file__).resolve().parents[3]
        self.marts_dir = self.repo_root / "data" / "marts"

    def _guard_data_access(self) -> None:
        if settings.database_url:
            raise DatabaseUnavailableError(
                "Postgres-oriented queries are designed but no PostgreSQL driver is installed in this runtime. "
                "Use local CSV fallback for MVP demo by setting FPI_USE_CSV_FALLBACK=true."
            )
        if not settings.use_csv_fallback:
            raise DatabaseUnavailableError(
                "PostgreSQL is not configured in this environment. Set FPI_DATABASE_URL for DB access or "
                "FPI_USE_CSV_FALLBACK=true for explicit local marts fallback."
            )

    def _read_csv(self, filename: str) -> list[dict]:
        path = self.marts_dir / filename
        if not path.exists():
            return []
        with path.open(newline="", encoding="utf-8") as file:
            return list(csv.DictReader(file))

    def _airport_from_iata(self, iata: str) -> dict:
        return {
            "iata": iata,
            "airport_name": f"{iata} (name unavailable in CSV fallback)",
            "city": None,
            "state": None,
            "country": "US",
        }

    def search_airports(self, query: str, limit: int = 10) -> list[dict]:
        self._guard_data_access()
        scores = self._read_csv("route_scores.csv")
        fares = self._read_csv("monthly_fares.csv")
        iatas = set()
        for row in [*scores, *fares]:
            route_key = row.get("route_key", "")
            if "-" in route_key:
                origin, destination = route_key.split("-", 1)
                iatas.add(origin)
                iatas.add(destination)
        results = [self._airport_from_iata(iata) for iata in sorted(iatas) if query in iata]
        return results[:limit]

    def get_route_explorer(self, origin_iata: str, limit: int = 25) -> list[dict]:
        self._guard_data_access()
        scores = self._read_csv("route_scores.csv")
        fares = self._read_csv("monthly_fares.csv")
        latest_by_route: dict[str, dict] = {}
        for row in scores:
            route = row.get("route_key", "")
            y, m = int(row.get("year", 0)), int(row.get("month", 0))
            prev = latest_by_route.get(route)
            if prev is None or (y, m) > (prev["_year"], prev["_month"]):
                latest_by_route[route] = {**row, "_year": y, "_month": m}

        latest_fare_by_route: dict[str, float] = {}
        fare_period: dict[str, tuple[int, int]] = {}
        for row in fares:
            route = row.get("route_key", "")
            y, m = int(row.get("year", 0)), int(row.get("month", 0))
            if route not in fare_period or (y, m) > fare_period[route]:
                fare_period[route] = (y, m)
                latest_fare_by_route[route] = float(row.get("avg_fare_usd", 0))

        output: list[dict] = []
        for route_key, score in latest_by_route.items():
            if "-" not in route_key:
                continue
            origin, destination = route_key.split("-", 1)
            if origin != origin_iata:
                continue
            output.append(
                {
                    "destination_iata": destination,
                    "destination_airport_name": f"{destination} (name unavailable in CSV fallback)",
                    "destination_city": None,
                    "destination_state": None,
                    "destination_country": "US",
                    "latest_route_attractiveness_score": float(score["route_attractiveness_score"])
                    if score.get("route_attractiveness_score")
                    else None,
                    "deal_signal": score.get("deal_signal"),
                    "latest_avg_fare_usd": latest_fare_by_route.get(route_key),
                    "avg_ontime_rate": None,
                    "avg_cancellation_rate": None,
                    "score_confidence": None,
                }
            )
        output.sort(key=lambda r: (r["latest_route_attractiveness_score"] is None, -(r["latest_route_attractiveness_score"] or 0)))
        return output[:limit]

    def get_route_detail(self, origin_iata: str, destination_iata: str) -> dict | None:
        self._guard_data_access()
        route_key = f"{origin_iata}-{destination_iata}"
        fares = [r for r in self._read_csv("monthly_fares.csv") if r.get("route_key") == route_key]
        scores = [r for r in self._read_csv("route_scores.csv") if r.get("route_key") == route_key]
        if not fares and not scores:
            return None
        fare_points = [
            {"year": int(r["year"]), "month": int(r["month"]), "avg_fare_usd": float(r["avg_fare_usd"])} for r in fares
        ]
        fare_points.sort(key=lambda f: (f["year"], f["month"]))
        cheapest = min(fare_points, key=lambda f: f["avg_fare_usd"]) if fare_points else None
        latest_score = None
        if scores:
            latest_raw = max(scores, key=lambda r: (int(r.get("year", 0)), int(r.get("month", 0))))
            latest_score = {
                "year": int(latest_raw.get("year", 0)),
                "month": int(latest_raw.get("month", 0)),
                "reliability_score": float(latest_raw["reliability_score"]) if latest_raw.get("reliability_score") else None,
                "fare_volatility": float(latest_raw["fare_volatility"]) if latest_raw.get("fare_volatility") else None,
                "route_attractiveness_score": float(latest_raw["route_attractiveness_score"])
                if latest_raw.get("route_attractiveness_score")
                else None,
                "deal_signal": latest_raw.get("deal_signal", "neutral"),
            }
        return {
            "route": {
                "origin_iata": origin_iata,
                "origin_airport_name": f"{origin_iata} (name unavailable in CSV fallback)",
                "origin_city": None,
                "origin_state": None,
                "origin_country": "US",
                "destination_iata": destination_iata,
                "destination_airport_name": f"{destination_iata} (name unavailable in CSV fallback)",
                "destination_city": None,
                "destination_state": None,
                "destination_country": "US",
            },
            "fares": fare_points,
            "reliability": [],
            "score": latest_score,
            "cheapest_month": cheapest,
        }

    def get_airport_context(self, iata: str) -> dict | None:
        self._guard_data_access()
        explore = self.get_route_explorer(origin_iata=iata, limit=5)
        search = self.search_airports(query=iata, limit=1)
        if not search and not explore:
            return None
        airport = search[0] if search else self._airport_from_iata(iata)
        return {"airport": airport, "enplanement": None, "related_routes": explore}
