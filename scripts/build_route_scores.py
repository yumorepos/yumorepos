"""Build route_scores mart placeholder from monthly_fares and reliability marts.

Input marts:
- data/marts/monthly_fares.csv
- data/marts/ontime_stats.csv
- data/marts/cancellations.csv

Output:
- data/marts/route_scores.csv (grain: route + year + month)

MVP scope note:
- This script intentionally does NOT implement advanced scoring formulas yet.
- It produces a stable route-month scaffold with conservative placeholder metrics,
  so downstream API/load logic has a consistent artifact.
"""

from __future__ import annotations

import argparse
import logging
from collections import defaultdict
from pathlib import Path

from pipeline_utils import marts_path, read_csv_rows, setup_logging, write_csv_rows

LOGGER = logging.getLogger("build_route_scores")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build route_scores scaffold mart")
    parser.add_argument("--fares-input", default=str(marts_path("monthly_fares.csv")))
    parser.add_argument("--ontime-input", default=str(marts_path("ontime_stats.csv")))
    parser.add_argument("--cancel-input", default=str(marts_path("cancellations.csv")))
    parser.add_argument("--output", default=str(marts_path("route_scores.csv")))
    parser.add_argument("--log-level", default="INFO")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    setup_logging(args.log_level)

    fares_rows = read_csv_rows(Path(args.fares_input))
    ontime_rows = read_csv_rows(Path(args.ontime_input))
    cancel_rows = read_csv_rows(Path(args.cancel_input))

    keys: set[tuple[str, int, int]] = set()
    for row in fares_rows:
        keys.add((row["route_key"], int(row["year"]), int(row["month"])))

    route_month_reliability = defaultdict(lambda: {"flights": 0, "ontime": 0, "cancel": 0})
    for row in ontime_rows:
        key = (row["route_key"], int(row["year"]), int(row["month"]))
        route_month_reliability[key]["flights"] += int(row["flights_total"])
        route_month_reliability[key]["ontime"] += int(row["flights_ontime"])
        keys.add(key)
    for row in cancel_rows:
        key = (row["route_key"], int(row["year"]), int(row["month"]))
        route_month_reliability[key]["cancel"] += int(row["cancellations_count"])
        keys.add(key)

    output_rows = []
    for route_key, year, month in sorted(keys):
        rel = route_month_reliability[(route_key, year, month)]
        flights = rel["flights"]
        reliability_score = ""
        if flights > 0:
            reliability_score = round(((rel["ontime"] - rel["cancel"]) / flights) * 100, 3)

        output_rows.append(
            {
                "route_key": route_key,
                "year": year,
                "month": month,
                "reliability_score": reliability_score,
                "fare_volatility": "",  # Planned metric
                "deal_signal": "neutral",  # Placeholder signal
                "route_attractiveness_score": "",  # Planned metric
            }
        )

    write_csv_rows(
        Path(args.output),
        output_rows,
        [
            "route_key",
            "year",
            "month",
            "reliability_score",
            "fare_volatility",
            "deal_signal",
            "route_attractiveness_score",
        ],
    )
    LOGGER.info("Wrote %s route_scores scaffold rows to %s", len(output_rows), args.output)


if __name__ == "__main__":
    main()
