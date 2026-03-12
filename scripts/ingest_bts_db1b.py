"""Ingest BTS DB1B fare extracts into canonical raw files.

Expected input:
- CSV with fields mapping to ORIGIN, DEST, YEAR, QUARTER or MONTH, and fare.

Output:
- data/raw/bts_db1b_raw.csv with canonical columns:
  origin_iata, destination_iata, year, month, fare_usd, passengers

Notes:
- DB1B is often quarterly. If only QUARTER is present, this script maps quarter to
  the first month of quarter (1, 4, 7, 10) as an explicit MVP approximation.
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from pipeline_utils import (
    DQReport,
    canonical_airport_code,
    make_route_key,
    normalize_numeric,
    parse_month,
    parse_year,
    raw_path,
    read_csv_rows,
    setup_logging,
    write_csv_rows,
)

LOGGER = logging.getLogger("ingest_bts_db1b")


QUARTER_TO_MONTH = {1: 1, 2: 4, 3: 7, 4: 10}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Normalize BTS DB1B CSV into raw layer")
    parser.add_argument("--input", required=True, help="Path to DB1B CSV extract")
    parser.add_argument("--output", default=str(raw_path("bts_db1b_raw.csv")), help="Output raw CSV path")
    parser.add_argument("--log-level", default="INFO")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    setup_logging(args.log_level)

    rows = read_csv_rows(Path(args.input))
    dq = DQReport()
    output_rows = []

    for row in rows:
        origin = canonical_airport_code(row.get("ORIGIN") or row.get("origin"))
        dest = canonical_airport_code(row.get("DEST") or row.get("destination"))
        year = parse_year(row.get("YEAR") or row.get("year"))

        month = parse_month(row.get("MONTH") or row.get("month"))
        if month is None:
            quarter_raw = row.get("QUARTER") or row.get("quarter")
            try:
                quarter = int(str(quarter_raw).strip())
            except (TypeError, ValueError):
                quarter = None
            month = QUARTER_TO_MONTH.get(quarter)

        fare = normalize_numeric(row.get("ITIN_FARE") or row.get("fare") or row.get("fare_usd"))
        passengers = normalize_numeric(row.get("PASSENGERS") or row.get("passengers"))

        if not origin or not dest:
            dq.warn("missing_airport_code")
            continue
        if not make_route_key(origin, dest):
            dq.warn("invalid_route_key")
            continue
        if year is None or month is None:
            dq.warn("invalid_year_month")
            continue
        if fare is None:
            dq.warn("missing_fare")
            continue

        output_rows.append(
            {
                "origin_iata": origin,
                "destination_iata": dest,
                "year": year,
                "month": month,
                "fare_usd": round(fare, 2),
                "passengers": int(passengers) if passengers is not None else "",
            }
        )

    write_csv_rows(
        Path(args.output),
        output_rows,
        ["origin_iata", "destination_iata", "year", "month", "fare_usd", "passengers"],
    )
    LOGGER.info("Wrote %s normalized rows to %s", len(output_rows), args.output)
    if dq.counts:
        LOGGER.warning("DQ warnings: %s", dq.as_dict())


if __name__ == "__main__":
    main()
