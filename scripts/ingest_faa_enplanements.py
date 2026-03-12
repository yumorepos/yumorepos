"""Ingest FAA airport enplanement data into canonical raw files.

Expected input:
- CSV with fields mapping to airport code, year, total enplanements.

Output:
- data/raw/faa_enplanements_raw.csv with canonical columns:
  airport_iata, year, total_enplanements

This script assumes local source files and performs conservative validation only.
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from pipeline_utils import (
    DQReport,
    canonical_airport_code,
    normalize_numeric,
    parse_year,
    raw_path,
    read_csv_rows,
    setup_logging,
    write_csv_rows,
)

LOGGER = logging.getLogger("ingest_faa_enplanements")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Normalize FAA enplanement CSV into raw layer")
    parser.add_argument("--input", required=True, help="Path to FAA enplanement CSV extract")
    parser.add_argument("--output", default=str(raw_path("faa_enplanements_raw.csv")), help="Output raw CSV path")
    parser.add_argument("--log-level", default="INFO")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    setup_logging(args.log_level)

    rows = read_csv_rows(Path(args.input))
    dq = DQReport()
    output_rows = []

    for row in rows:
        airport = canonical_airport_code(row.get("IATA") or row.get("airport_iata") or row.get("AIRPORT"))
        year = parse_year(row.get("YEAR") or row.get("year"))
        enplanements = normalize_numeric(row.get("TOTAL_ENPLANEMENTS") or row.get("enplanements") or row.get("total_enplanements"))

        if not airport:
            dq.warn("missing_airport_code")
            continue
        if year is None:
            dq.warn("invalid_year")
            continue
        if enplanements is None or enplanements < 0:
            dq.warn("invalid_enplanements")
            continue

        output_rows.append(
            {
                "airport_iata": airport,
                "year": year,
                "total_enplanements": int(enplanements),
            }
        )

    write_csv_rows(Path(args.output), output_rows, ["airport_iata", "year", "total_enplanements"])
    LOGGER.info("Wrote %s normalized rows to %s", len(output_rows), args.output)
    if dq.counts:
        LOGGER.warning("DQ warnings: %s", dq.as_dict())


if __name__ == "__main__":
    main()
