from fastapi import FastAPI

from app.api.v1.routes import commodities, markets, prices

app = FastAPI(
    title="Zimbabwe Commodity Prices API",
    version="0.1.0",
    description=(
        "Daily-updating commodity price platform for Zimbabwe. "
        "This backend exposes a versioned REST API over a PostgreSQL data store."
    ),
)


@app.get("/health", tags=["meta"])
async def health_check() -> dict:
    """Lightweight health endpoint for load balancers and uptime checks."""

    return {"status": "ok"}


app.include_router(commodities.router, prefix="/api/v1")
app.include_router(markets.router, prefix="/api/v1")
app.include_router(prices.router, prefix="/api/v1")
