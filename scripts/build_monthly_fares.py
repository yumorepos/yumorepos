"""Build `monthly_fares` mart from normalized DB1B raw data.

Input:
- data/raw/bts_db1b_raw.csv

Output:
- data/marts/monthly_fares.csv
  Grain: route + year + month

MVP behavior:
- route key is `ORIGIN-DEST`
- average fare is simple arithmetic mean of normalized records
- passengers are summed when present
"""

from __future__ import annotations

import argparse
import logging
from collections import defaultdict
from pathlib import Path

from pipeline_utils import DQReport, marts_path, raw_path, read_csv_rows, setup_logging, staging_path, write_csv_rows

LOGGER = logging.getLogger("build_monthly_fares")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Aggregate monthly fares mart")
    parser.add_argument("--input", default=str(raw_path("bts_db1b_raw.csv")), help="Canonical DB1B raw input")
    parser.add_argument("--staging-output", default=str(staging_path("db1b_normalized.csv")), help="Normalized staging snapshot")
    parser.add_argument("--output", default=str(marts_path("monthly_fares.csv")), help="monthly_fares mart output")
    parser.add_argument("--log-level", default="INFO")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    setup_logging(args.log_level)
    rows = read_csv_rows(Path(args.input))

    dq = DQReport()
    grouped: dict[tuple[str, int, int], dict[str, float]] = defaultdict(lambda: {"fare_sum": 0.0, "fare_count": 0.0, "passengers": 0.0})
    staging_rows = []

    for row in rows:
        route_key = f"{row['origin_iata']}-{row['destination_iata']}"
        try:
            year = int(row["year"])
            month = int(row["month"])
            fare = float(row["fare_usd"])
        except (TypeError, ValueError, KeyError):
            dq.warn("malformed_record")
            continue

        staging_rows.append({"route_key": route_key, "year": year, "month": month, "fare_usd": fare, "passengers": row.get("passengers", "")})

        key = (route_key, year, month)
        grouped[key]["fare_sum"] += fare
        grouped[key]["fare_count"] += 1
        if str(row.get("passengers", "")).strip() != "":
            try:
                grouped[key]["passengers"] += float(row["passengers"])
            except ValueError:
                dq.warn("invalid_passengers")

    output_rows = []
    for (route_key, year, month), agg in sorted(grouped.items()):
        if agg["fare_count"] == 0:
            dq.warn("empty_aggregate")
            continue
        output_rows.append(
            {
                "route_key": route_key,
                "year": year,
                "month": month,
                "avg_fare_usd": round(agg["fare_sum"] / agg["fare_count"], 2),
                "passengers_estimated": int(agg["passengers"]) if agg["passengers"] else "",
            }
        )

    write_csv_rows(Path(args.staging_output), staging_rows, ["route_key", "year", "month", "fare_usd", "passengers"])
    write_csv_rows(Path(args.output), output_rows, ["route_key", "year", "month", "avg_fare_usd", "passengers_estimated"])
    LOGGER.info("Wrote %s staging rows to %s", len(staging_rows), args.staging_output)
    LOGGER.info("Wrote %s monthly_fares rows to %s", len(output_rows), args.output)
    if dq.counts:
        LOGGER.warning("DQ warnings: %s", dq.as_dict())


if __name__ == "__main__":
    main()
