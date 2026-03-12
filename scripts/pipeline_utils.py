"""Shared utilities for MVP batch data pipeline scripts.

This module intentionally keeps dependencies minimal (stdlib only) so scripts can run
in lightweight environments. It provides:
- consistent logging setup
- CSV helpers
- normalization helpers for airport/airline/date/route fields
- simple data-quality warning tracking
- canonical data layer path helpers (raw/staging/marts)
"""

from __future__ import annotations

import csv
import logging
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
STAGING_DIR = DATA_DIR / "staging"
MARTS_DIR = DATA_DIR / "marts"


@dataclass
class DQReport:
    """Collects simple warning counters for malformed or missing values."""

    counts: Counter[str] = field(default_factory=Counter)

    def warn(self, key: str) -> None:
        self.counts[key] += 1

    def as_dict(self) -> dict[str, int]:
        return dict(self.counts)


def setup_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def ensure_parent_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv_rows(path: Path, rows: Iterable[dict], fieldnames: list[str]) -> None:
    ensure_parent_dir(path)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def canonical_airport_code(value: str | None) -> str | None:
    if not value:
        return None
    v = value.strip().upper()
    return v if len(v) == 3 and v.isalpha() else None


def canonical_airline_code(value: str | None) -> str | None:
    if not value:
        return None
    v = value.strip().upper()
    return v if 2 <= len(v) <= 3 and v.isalnum() else None


def parse_year(value: str | None) -> int | None:
    if value is None:
        return None
    try:
        y = int(str(value).strip())
        return y if 1990 <= y <= 2100 else None
    except ValueError:
        return None


def parse_month(value: str | None) -> int | None:
    if value is None:
        return None
    try:
        m = int(str(value).strip())
        return m if 1 <= m <= 12 else None
    except ValueError:
        return None


def make_route_key(origin_iata: str | None, destination_iata: str | None) -> str | None:
    if not origin_iata or not destination_iata:
        return None
    if origin_iata == destination_iata:
        return None
    return f"{origin_iata}-{destination_iata}"


def normalize_numeric(value: str | None) -> float | None:
    if value is None or str(value).strip() == "":
        return None
    try:
        return float(str(value).replace(",", "").strip())
    except ValueError:
        return None


def raw_path(filename: str) -> Path:
    return RAW_DIR / filename


def staging_path(filename: str) -> Path:
    return STAGING_DIR / filename


def marts_path(filename: str) -> Path:
    return MARTS_DIR / filename
