# ✈️ Flight Price Intelligence Lab

A full-stack aviation analytics product that evaluates airline route attractiveness using historical airfare trends, operational reliability signals, and airport context.

This project demonstrates how public aviation datasets can be transformed into a transparent decision-support tool for exploratory route intelligence.

---

# Product Preview

## Route Explorer

![Route Explorer](docs/screenshots/route-explorer.png)

## Route Detail

![Route Detail](docs/screenshots/route-detail.png)

---

# Why This Project Exists

Airfare search tools focus on **finding flights**, not **understanding routes**.

Flight Price Intelligence Lab explores a different question:

> *How attractive is this route historically?*

The app surfaces:

* historical fare patterns
* reliability signals
* route-relative pricing signals
* airport market context
* transparent heuristic scoring

The goal is **exploratory analytics**, not operational forecasting.

---

# Key Features

### Route Explorer

Search an origin airport to explore historically attractive routes.

Each route card shows:

* route attractiveness score
* deal signal vs historical baseline
* latest observed fare insight
* reliability cues (when available)
* score confidence

---

### Route Detail View

Deep-dive analytics for a specific route.

Includes:

* score breakdown
* cheapest observed month
* fare trend visualization
* reliability trend
* airport context
* methodology explanation

---

### Transparent Data Provenance

The interface clearly shows:

* data source
* fallback mode
* coverage completeness

This prevents users from over-interpreting thin data.

---

# Architecture

```
BTS + FAA datasets
        │
        ▼
Python ETL pipeline
scripts/
        │
        ▼
Postgres analytics schema
monthly_fares
ontime_stats
route_scores
        │
        ▼
FastAPI analytics API
backend/
        │
        ▼
Next.js product UI
frontend/
```

---

# Technology Stack

Frontend

* Next.js
* TypeScript
* Component-driven UI

Backend

* FastAPI
* Python

Data / Analytics

* Python + Pandas
* SQL analytics modeling

Database

* PostgreSQL

Datasets

* BTS On-Time Performance
* BTS DB1B Ticket Sample
* FAA Airport Enplanements

---

# Data Sources

### BTS On-Time Performance

Used to calculate operational reliability metrics.

### BTS DB1B

Used for historical fare trend analysis.

### FAA Enplanement Data

Provides airport size and passenger context.

---

# Methodology (Simplified)

Route attractiveness is a heuristic blend of:

```
route_score =
  45% price attractiveness
  35% operational reliability
  20% price stability
```

Deal signals compare current observed fare against the route’s historical baseline.

The system intentionally avoids predictive claims.

---

# Local Development

Start backend:

```bash
cd backend
uvicorn app.main:app --reload
```

Start frontend:

```bash
cd frontend
npm install
npm run dev
```

Visit:

```
http://localhost:3000
```

---

# Current Project Status

This project is a **portfolio-grade MVP**, not a production system.

Implemented:

* analytics schema
* ETL pipeline scripts
* heuristic route scoring
* FastAPI analytics API
* Next.js product UI

Not implemented:

* automated data refresh orchestration
* production monitoring
* calibrated forecasting models
* authentication
* infrastructure hardening

---

# Future Improvements

Possible extensions:

* automated dataset ingestion
* richer reliability metrics
* forecast models for price seasonality
* airline-level performance analysis
* global route coverage

---

# Author

Built by **Yumo**
Aviation analytics enthusiast and data-driven product builder.


# Architecture Overview

```
Public Aviation Data
(BTS / FAA)
        │
        ▼
Python ETL Pipeline
scripts/
        │
        ▼
Analytics Tables
Postgres
───────────────
airports
routes
monthly_fares
ontime_stats
route_scores
───────────────
        │
        ▼
FastAPI Service
backend/
        │
        ▼
Next.js Product UI
frontend/
        │
        ▼
User Interface
Route Explorer
Route Detail
```
