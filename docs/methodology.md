# Methodology (MVP Data Pipeline Phase)

## Product intent
Provide route-level flight intelligence from public, explainable datasets without pretending real-time API coverage.

## Approved MVP sources
1. BTS On-Time Performance
2. BTS DB1B
3. FAA airport enplanement data

OpenSky is intentionally excluded from MVP implementation.

## Pipeline methodology

### Step A: Source ingestion (raw)
- Read local source extracts in CSV form.
- Apply minimal canonical field naming and type normalization.
- Preserve source semantics and avoid heavy transformation at this stage.

### Step B: Standardization (staging)
- Normalize route key format (`ORIGIN-DEST`).
- Validate year/month fields.
- Keep one normalized record per source observation for traceability.

### Step C: Analytical aggregation (marts)
- Build mart tables at the same grain as schema v1:
  - `monthly_fares`: route + year + month
  - `ontime_stats`: route + airline + year + month
  - `cancellations`: route + airline + year + month
  - `route_scores`: route + year + month (scaffold)
- Keep transformations transparent and inspectable.

### Step D: Database load
- Upsert dimensions first (`airports`, `airlines`, `routes`).
- Upsert facts second (`monthly_fares`, `ontime_stats`, `cancellations`, `airport_enplanements`, `route_scores`).
- Support dry-run validation before write execution.

## Data contracts and conventions
- `airport_iata`, `origin_iata`, `destination_iata`: uppercase 3-letter IATA codes
- `carrier_code`: uppercase 2–3 alphanumeric carrier code
- `year`: four-digit integer; `month`: integer 1–12
- `route_key`: `ORIGIN-DEST` used in file-based layers

## Data quality rules (MVP)
Rows are skipped (with warnings) when they break essential contract rules:
- missing/invalid airport codes
- missing carrier code for on-time dataset
- invalid year/month
- missing or malformed fare records
- malformed route keys (including same-origin/destination)

Rows with sparse optional fields are retained when possible and flagged:
- missing `ARR_DEL15`
- missing `CANCELLED`

## Known dataset limitations (explicit)
- DB1B is commonly distributed quarterly; month mapping may be approximate in MVP when monthly fields are unavailable.
- On-time extracts vary by selected BTS columns; delay-minute metrics may be absent.
- FAA airport identifiers may require additional crosswalks for full production coverage.

## Implemented now vs planned

### Implemented now
- Scripted batch foundation for raw ingestion, staging normalization, marts builds, and DB loading.
- Structured logging and basic DQ warning counters.

### Planned later
- More robust airport/carrier crosswalk handling.
- Advanced scoring formulas (`fare_volatility`, `deal_signal`, `route_attractiveness_score`).
- Better operational monitoring and reproducibility metadata.

## Analytics metric status
The following remain planned analytics outputs (not finalized formulas in this phase):
- `cheapest_month`
- `fare_volatility`
- `reliability_score` (partially scaffolded in route_scores)
- `deal_signal` (placeholder default)
- `route_attractiveness_score`
