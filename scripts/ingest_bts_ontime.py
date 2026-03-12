"""Ingest BTS On-Time Performance extracts into canonical raw files.

Expected input:
- CSV with fields that can map to ORIGIN, DEST, YEAR, MONTH,
  CARRIER/OP_UNIQUE_CARRIER, ARR_DEL15, CANCELLED.

Output:
- data/raw/bts_ontime_raw.csv with canonical columns:
  origin_iata, destination_iata, carrier_code, year, month, arr_del15, cancelled

This is an MVP local-file ingester. Remote download automation is intentionally out of scope.
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from pipeline_utils import (
    DQReport,
    canonical_airline_code,
    canonical_airport_code,
    make_route_key,
    parse_month,
    parse_year,
    raw_path,
    read_csv_rows,
    setup_logging,
    write_csv_rows,
)

LOGGER = logging.getLogger("ingest_bts_ontime")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Normalize BTS on-time CSV into raw layer")
    parser.add_argument("--input", required=True, help="Path to BTS on-time CSV extract")
    parser.add_argument("--output", default=str(raw_path("bts_ontime_raw.csv")), help="Output raw CSV path")
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
        carrier = canonical_airline_code(row.get("OP_UNIQUE_CARRIER") or row.get("CARRIER") or row.get("carrier"))
        year = parse_year(row.get("YEAR") or row.get("year"))
        month = parse_month(row.get("MONTH") or row.get("month"))

        if not origin or not dest:
            dq.warn("missing_airport_code")
            continue
        if not make_route_key(origin, dest):
            dq.warn("invalid_route_key")
            continue
        if not carrier:
            dq.warn("missing_carrier_code")
            continue
        if year is None or month is None:
            dq.warn("invalid_year_month")
            continue

        output_rows.append(
            {
                "origin_iata": origin,
                "destination_iata": dest,
                "carrier_code": carrier,
                "year": year,
                "month": month,
                "arr_del15": row.get("ARR_DEL15", ""),
                "cancelled": row.get("CANCELLED", ""),
            }
        )

    write_csv_rows(
        Path(args.output),
        output_rows,
        ["origin_iata", "destination_iata", "carrier_code", "year", "month", "arr_del15", "cancelled"],
    )
    LOGGER.info("Wrote %s normalized rows to %s", len(output_rows), args.output)
    if dq.counts:
        LOGGER.warning("DQ warnings: %s", dq.as_dict())


if __name__ == "__main__":
    main()
