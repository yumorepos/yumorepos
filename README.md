# Flight Price Intelligence Lab

Flight Price Intelligence Lab is a portfolio-grade product prototype that turns public aviation datasets into **route-level decision intelligence**.

It is intentionally built as an honest MVP: strong enough to demonstrate product thinking + analytics engineering, while being explicit about current limits.

## What this project is

A full-stack analytics app where users can:
- Search origin airports
- Explore destination routes with a composite route score
- Inspect route-level fare/reliability history
- Review data provenance, confidence, and methodology caveats

## Why it matters

Aviation and travel decisions often mix imperfect operational data, noisy fare signals, and stakeholder pressure for clear recommendations. This project demonstrates how to:
- Build trustworthy analytics UX under imperfect data conditions
- Explain scoring logic without pretending model certainty
- Keep product narrative and technical implementation aligned

## What makes it different

- **Explainable scoring, not black-box theater:** route scoring is deterministic and documented.
- **Trust-first UX:** provenance, fallback mode, and incomplete coverage are surfaced.
- **End-to-end delivery:** data pipeline foundation, API contracts, and product UI shipped together.
- **Portfolio realism:** docs describe what works, what is partial, and what is missing.

## Architecture at a glance

- **Frontend:** Next.js + TypeScript (`frontend/`)
- **Backend:** FastAPI (`backend/`)
- **Data pipeline:** Python batch scripts (`scripts/`)
- **Storage:** PostgreSQL schema v1 (`sql/schema.sql`)
- **Data lifecycle:** `data/raw` → `data/staging` → `data/marts`

For deeper detail, see `docs/architecture.md`.

## Data sources (MVP scope)

1. BTS DB1B (fare aggregates)
2. BTS On-Time Performance (reliability/cancellations)
3. FAA enplanements (airport context)

No real-time market feed is currently implemented.

## Methodology summary

The product reports two primary route-level signals:

- **Route score (0–100):** heuristic blend of fare attractiveness, reliability, and fare stability.
- **Deal signal:** relative pricing label (`strong_deal`, `deal`, `neutral`, `expensive`) versus route historical baseline.

These are directional intelligence signals, not price predictions or revenue forecasts.

For details and caveats, see `docs/methodology.md`.

## Current implementation status

### Definitely implemented
- Route Explorer and Route Detail flows with score + trend views
- Provenance metadata surfaced in API and UI
- FastAPI read endpoints for airports, routes, context, and methodology
- MVP batch pipeline foundation from raw/staging/marts to Postgres load

### Partially implemented
- Reliability coverage varies by route/month in fallback mode
- Airport metadata completeness depends on loaded slices
- Score confidence is useful but not yet deeply diagnostic in UI

### Not implemented yet
- Production orchestration/scheduling
- Real-time/near-real-time refresh
- Auth, role-based access, observability, SLOs
- Statistical calibration framework for score drift

## Local run instructions

### 1) Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# For MVP demo mode (works without Postgres), enable CSV fallback:
echo "FPI_USE_CSV_FALLBACK=true" >> .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2) Frontend

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

App URL: `http://localhost:3000`

By default, frontend requests `/api/*` and Next.js rewrites to backend `http://127.0.0.1:8000` for local development.

### 3) Quick API checks

```bash
curl http://localhost:8000/health
curl "http://localhost:8000/airports/search?q=jfk"
curl "http://localhost:8000/routes/explore?origin=JFK"
curl http://localhost:8000/routes/JFK/LAX
curl http://localhost:8000/airports/JFK/context
curl http://localhost:8000/meta/methodology
```

## Limitations (explicit)

- Historical coverage is limited to loaded datasets/slices.
- Fallback CSV mode can be incomplete and should be treated carefully.
- Scoring is heuristic and not validated for operational deployment decisions.
- UX is portfolio-polished, but production non-functionals are still missing.

## Roadmap

See `docs/roadmap.md` for the phased path from MVP to production-grade platform.

## Why this is a strong portfolio project

This project demonstrates the intersection of:
- Product strategy (decision-oriented UX)
- Analytics architecture (traceable marts and data contracts)
- Full-stack execution (frontend + backend integration)
- Technical honesty (clear caveats, scope boundaries, and next steps)

It is not positioned as “production-ready.” It is positioned as **high-quality, credible, and thoughtfully scoped**.
