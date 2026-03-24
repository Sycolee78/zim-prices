# Zimbabwe Daily Commodity Prices Platform

Daily-updating commodity price platform for Zimbabwe, with:

- **Ingestion pipeline** for official sources (ZMX, ZERA, RBZ, FPMA, licensed APIs like Statista)
- **PostgreSQL-backed data model** with strong provenance and deduplication
- **FastAPI REST API** for querying prices and metadata
- **Frontend dashboard** (Next.js) for visualization and exploration

This repo follows a pipeline-centered architecture: scheduled jobs fetch raw artifacts (HTML/PDF/API responses), normalize them into `price_observation` facts, and expose them via a versioned API and web UI.

> Initial scaffold only. Implementation will be filled in phase by phase (ingestion, API, frontend, ops).