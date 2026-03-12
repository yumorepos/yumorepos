"""Build `ontime_stats` and `cancellations` marts from normalized BTS on-time raw data.

Input:
- data/raw/bts_ontime_raw.csv

Outputs:
- data/marts/ontime_stats.csv      (grain: route + airline + year + month)
- data/marts/cancellations.csv     (grain: route + airline + year + month)

MVP behavior:
- Flights are counted as row-level records in the input extract.
- ontime_rate uses ARR_DEL15 where 0 means on-time, 1 means delayed 15+ minutes.
- cancellation_rate uses CANCELLED where 1 means cancelled.
"""

from __future__ import annotations

import argparse
import logging
from collections import defaultdict
from pathlib import Path

from pipeline_utils import DQReport, marts_path, raw_path, read_csv_rows, setup_logging, staging_path, write_csv_rows

LOGGER = logging.getLogger("build_ontime_stats")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Aggregate on-time and cancellation marts")
    parser.add_argument("--input", default=str(raw_path("bts_ontime_raw.csv")), help="Canonical BTS on-time raw input")
    parser.add_argument("--staging-output", default=str(staging_path("ontime_normalized.csv")), help="Normalized staging snapshot")
    parser.add_argument("--ontime-output", default=str(marts_path("ontime_stats.csv")), help="ontime_stats mart output")
    parser.add_argument("--cancel-output", default=str(marts_path("cancellations.csv")), help="cancellations mart output")
    parser.add_argument("--log-level", default="INFO")
    return parser.parse_args()


def parse_binary(value: str | None) -> int | None:
    if value is None or str(value).strip() == "":
        return None
    try:
        v = int(float(str(value).strip()))
        return v if v in (0, 1) else None
    except ValueError:
        return None


def main() -> None:
    args = parse_args()
    setup_logging(args.log_level)
    rows = read_csv_rows(Path(args.input))

    dq = DQReport()
    grouped = defaultdict(lambda: {"flights_total": 0, "flights_ontime": 0, "cancel_count": 0, "delay_obs": 0})
    staging_rows = []

    for row in rows:
        try:
            route_key = f"{row['origin_iata']}-{row['destination_iata']}"
            airline_code = row["carrier_code"]
            year = int(row["year"])
            month = int(row["month"])
        except (KeyError, ValueError):
            dq.warn("malformed_record")
            continue

        staging_rows.append({"route_key": route_key, "carrier_code": airline_code, "year": year, "month": month, "arr_del15": row.get("arr_del15", ""), "cancelled": row.get("cancelled", "")})

        key = (route_key, airline_code, year, month)
        grouped[key]["flights_total"] += 1

        arr_del15 = parse_binary(row.get("arr_del15"))
        if arr_del15 is None:
            dq.warn("missing_arr_del15")
        else:
            grouped[key]["delay_obs"] += 1
            if arr_del15 == 0:
                grouped[key]["flights_ontime"] += 1

        cancelled = parse_binary(row.get("cancelled"))
        if cancelled is None:
            dq.warn("missing_cancelled")
        elif cancelled == 1:
            grouped[key]["cancel_count"] += 1

    ontime_rows = []
    cancel_rows = []

    for (route_key, airline_code, year, month), agg in sorted(grouped.items()):
        flights_total = agg["flights_total"]
        ontime_rows.append(
            {
                "route_key": route_key,
                "carrier_code": airline_code,
                "year": year,
                "month": month,
                "flights_total": flights_total,
                "flights_ontime": agg["flights_ontime"],
                "ontime_rate": round(agg["flights_ontime"] / flights_total, 4) if flights_total else "",
                "avg_arrival_delay_minutes": "",  # Placeholder until delay-minute field is standardized
            }
        )

        cancel_rows.append(
            {
                "route_key": route_key,
                "carrier_code": airline_code,
                "year": year,
                "month": month,
                "flights_total": flights_total,
                "cancellations_count": agg["cancel_count"],
                "cancellation_rate": round(agg["cancel_count"] / flights_total, 4) if flights_total else "",
            }
        )

    write_csv_rows(Path(args.staging_output), staging_rows, ["route_key", "carrier_code", "year", "month", "arr_del15", "cancelled"])

    write_csv_rows(
        Path(args.ontime_output),
        ontime_rows,
        [
            "route_key",
            "carrier_code",
            "year",
            "month",
            "flights_total",
            "flights_ontime",
            "ontime_rate",
            "avg_arrival_delay_minutes",
        ],
    )
    write_csv_rows(
        Path(args.cancel_output),
        cancel_rows,
        ["route_key", "carrier_code", "year", "month", "flights_total", "cancellations_count", "cancellation_rate"],
    )

    LOGGER.info("Wrote %s staging rows to %s", len(staging_rows), args.staging_output)
    LOGGER.info("Wrote %s ontime_stats rows to %s", len(ontime_rows), args.ontime_output)
    LOGGER.info("Wrote %s cancellations rows to %s", len(cancel_rows), args.cancel_output)
    if dq.counts:
        LOGGER.warning("DQ warnings: %s", dq.as_dict())


if __name__ == "__main__":
    main()
