# Implementation Plan - Zimbabwe Commodity Prices Platform

## Phase 0 - Repo & Backend Skeleton ✅

**Completed**
- Monorepo created (`zim-prices`) with `backend/`, `scrapers/`, `frontend/`, `docs/`.
- FastAPI app scaffolded in `backend/app/main.py` with `/health` endpoint.
- Docker Compose stack for local dev with `db` (Postgres) and `api` services.
- DB session + SQLAlchemy `Base` in `backend/app/db/session.py`.
- Core models defined in `backend/app/db/models/`:
  - `source.py` → `Source`, `SourceEndpoint`
  - `commodity.py` → `Commodity`, `CommodityVariant`
  - `region_market.py` → `Region`, `Market`
  - `currency_unit.py` → `Currency`, `Unit`
  - `scrape.py` → `ScrapeRun`, `RawArtifact`
  - `price_observation.py` → `PriceObservation`
- Alembic initialized in `backend/app/db/migrations/` and wired to `Base.metadata`.

## Phase 1 - Public Read API (in progress) 🚧

**Completed in this phase**
- Pydantic schemas under `backend/app/api/v1/schemas/`:
  - `commodity.py` → `CommodityOut`, `CommodityVariantOut`
  - `market.py` → `RegionOut`, `MarketOut`
  - `price.py` → `PriceObservationOut`, `LatestPriceOut`, `PriceQuery`
- FastAPI routers under `backend/app/api/v1/routes/`:
  - `commodities.py` → `GET /api/v1/commodities`
  - `markets.py` → `GET /api/v1/markets`
  - `prices.py` →
    - `GET /api/v1/prices` (raw observations with filters)
    - `GET /api/v1/prices/latest` (latest observation for a commodity + optional market)
- Routers included in `app.main` with prefix `/api/v1`.

**Remaining in this phase**
- Finish Alembic autogen migration for the core schema (clean any remaining `| None` typing issues and run `alembic revision --autogenerate` + `alembic upgrade head`).
- Add basic error envelope / problem-details style responses (optional polish).
- Add minimal seed script or fixtures to test endpoints quickly.

## Phase 2 - Ingestion (ZMX first) ⏳

**Planned**
- `scrapers/zim_prices_scrapers/sources/zmx.py`:
  - Fetch `https://system.zmx.co.zw/zmxwebpage/ATSCommo.aspx`.
  - Parse Market Watch / Recent Orders tables.
  - Normalize contract codes (`MAIZE/B/HRE/USD` → commodity/variant/market/currency).
- `scrapers/zim_prices_scrapers/normalization/`:
  - Unit and currency normalization helpers.
- `scrapers/zim_prices_scrapers/orchestration/jobs.py`:
  - `run_zmx_daily()` entry point to run the scraper and (eventually) upsert into `price_observation`.

## Phase 3 - Scheduler & Automation ⏳

**Planned**
- `.github/workflows/scrape-daily.yml`:
  - On schedule and manual dispatch.
  - Checkout repo, set up Python, install scraper package.
  - Call `python -m zim_prices_scrapers.orchestration.jobs run_zmx_daily`.
- Later: move scheduling to production infra (K8s CronJob / EventBridge) when ready.

## Phase 4 - Frontend (Next.js) ⏳

**Planned**
- Next.js app (app router) in `frontend/app/`:
  - `page.tsx` → dashboard using `/api/v1/prices/latest`.
  - `commodities/page.tsx` → list from `/api/v1/commodities`.
  - `commodities/[slug]/page.tsx` → detail view using `/api/v1/prices`.
  - `markets/[code]/page.tsx` → market detail.
- API client helpers in `frontend/app/lib/api.ts`.

## Phase 5 - Hardening & Expansion ⏳

**Planned**
- Auth & API keys for higher rate limits and admin endpoints.
- Additional ingestors (ZERA, RBZ PDFs, FPMA, tariffs).
- Monitoring/alerting, logging, and data quality checks.

---

Use this file as the canonical scaffold:
- When you start a new session, scan this to see what exists and what phase to work on.
- Update the checklists as you complete tasks (e.g., marking "Remaining" items as done and moving them up).
