# Flight Price Intelligence Lab

Flight Price Intelligence Lab is a portfolio-first aviation analytics product scaffold focused on turning public aviation datasets into route-level decision support.

## Why this project exists

This repository is intended to demonstrate:
- Travel-domain understanding (fares, routes, reliability, airport context)
- Product-oriented analytics design
- Full-stack engineering across frontend, backend, and data workflows

## Target stack

- **Frontend:** Next.js + TypeScript
- **Backend:** FastAPI (Python)
- **Data/Analytics:** Python, Pandas, SQL
- **Database:** PostgreSQL
- **Charts (planned):** Recharts or Plotly

## Planned MVP (2–3 week scope)

- Route search and route detail foundation
- Historical fare trend view (from curated datasets)
- Reliability summary (on-time and cancellations)
- Airport context panel
- Early route/deal score placeholders

## Current repository status

This repository currently contains **project foundation scaffolding only**:
- Monorepo directory layout
- Minimal Next.js app skeleton
- Minimal FastAPI app skeleton with health endpoint
- Implemented MVP batch pipeline foundation in `scripts/` (raw/staging/marts/load)
- Implemented Postgres analytics schema v1 (`sql/schema.sql`)
- Initial project documentation skeleton

Analytics logic, full product UI, and production hardening are intentionally not implemented yet.

## High-level architecture

- `frontend/` — Next.js app shell and UI foundation
- `backend/` — FastAPI app shell and API foundation
- `data/` — raw/staging/marts directories for data lifecycle
- `scripts/` — MVP batch ingestion, transforms, and Postgres load scripts
- `sql/` — schema definition (MVP analytics v1)
- `docs/` — architecture, methodology, roadmap, and data dictionary drafts

## Local setup (only for what exists today)

### Frontend

```bash
cd frontend
npm install
npm run dev
```

App runs at `http://localhost:3000`.

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Health check endpoint:

```bash
curl http://localhost:8000/health
```

## Next steps

- Validate pipeline scripts against real BTS/FAA source extracts
- Implement ingestion scripts for selected public datasets
- Build derived analytics tables and API endpoints
- Implement MVP frontend route intelligence views
