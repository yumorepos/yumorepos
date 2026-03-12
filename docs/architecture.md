# Architecture (MVP Pipeline Foundation)

## Overview
- **Frontend:** Next.js (scaffold only)
- **Backend:** FastAPI (scaffold only)
- **Data pipeline:** Python batch scripts in `scripts/`
- **Database:** PostgreSQL schema v1 in `sql/schema.sql`

This document covers the implemented MVP data pipeline foundation only.

## Data flow by layer

### 1) Raw layer (`data/raw/`)
Purpose: hold source-aligned, lightly normalized extracts from approved MVP sources.

Produced by:
- `scripts/ingest_bts_ontime.py` → `data/raw/bts_ontime_raw.csv`
- `scripts/ingest_bts_db1b.py` → `data/raw/bts_db1b_raw.csv`
- `scripts/ingest_faa_enplanements.py` → `data/raw/faa_enplanements_raw.csv`

### 2) Staging layer (`data/staging/`)
Purpose: standardize route/date and selected operational fields before mart aggregation.

Produced by:
- `scripts/build_monthly_fares.py` → `data/staging/db1b_normalized.csv`
- `scripts/build_ontime_stats.py` → `data/staging/ontime_normalized.csv`

### 3) Marts layer (`data/marts/`)
Purpose: schema-aligned analytical datasets at defined table grains.

Produced by:
- `scripts/build_monthly_fares.py` → `data/marts/monthly_fares.csv`
- `scripts/build_ontime_stats.py` → `data/marts/ontime_stats.csv`, `data/marts/cancellations.csv`
- `scripts/build_route_scores.py` → `data/marts/route_scores.csv` (scaffold metrics)

### 4) Postgres load
Purpose: upsert dimensions and facts into schema v1.

Executed by:
- `scripts/load_postgres.py`

Flow inside loader:
1. Read mart/raw files.
2. Derive dimensions (`airports`, `airlines`, `routes`) from `route_key` and source codes.
3. Upsert facts (`monthly_fares`, `ontime_stats`, `cancellations`, `airport_enplanements`, `route_scores`).

## Source-to-table mapping

- **BTS DB1B**
  - Supports: `monthly_fares`
  - Path: raw DB1B extract → staging normalized fares → route-month aggregation.

- **BTS On-Time Performance**
  - Supports: `ontime_stats`, `cancellations`
  - Path: raw on-time extract → staging normalized records → route-carrier-month aggregation.

- **FAA Enplanements**
  - Supports: `airport_enplanements`
  - Path: raw normalized enplanement file loaded as airport-year context.

- **Derived score scaffold**
  - Supports: `route_scores`
  - Path: marts inputs merged by route-month into placeholder score output.

## Naming conventions
- **Airport code:** `airport_iata`, `origin_iata`, `destination_iata` (uppercase 3-letter IATA)
- **Airline code:** `carrier_code` (2–3 alphanumeric carrier code)
- **Time fields:** `year` (4-digit), `month` (1–12)
- **Route key in files:** `route_key` = `ORIGIN-DEST` (e.g., `JFK-LAX`)
- **File naming:** source-aligned lower snake case, suffix `_raw.csv` in raw layer

## Data-quality checks implemented in scripts
- Missing/invalid airport codes
- Missing carrier codes (on-time)
- Invalid year/month values
- Missing or malformed fare values
- Malformed records that cannot map to route grain
- Sparse operational fields (`ARR_DEL15`, `CANCELLED`) flagged as warnings

Warnings are logged; invalid rows are skipped.

## What is implemented now
- Script-level ingestion/normalization foundation for approved MVP datasets.
- Batch transformations from raw → staging → marts.
- Simple Postgres loader with `--dry-run` mode and executable mode via `psycopg`.

## What is scaffold only
- `build_route_scores.py` uses conservative placeholder metric fields for parts of scoring.
- `avg_arrival_delay_minutes` is left blank pending standardized source mapping.

## What is not implemented yet
- Automated source download/auth workflows.
- Orchestration/scheduling (intentionally excluded for MVP).
- Advanced scoring formulas and production-grade observability.
- API-serving layer for mart outputs.
