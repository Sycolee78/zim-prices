from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel


class PriceObservationOut(BaseModel):
    id: UUID
    commodity_variant_id: UUID
    market_id: UUID
    source_id: UUID
    price_date: date
    price_type: str
    price: float | None = None
    price_bid: float | None = None
    price_ask: float | None = None
    volume: float | None = None
    turnover: float | None = None
    currency_id: UUID
    unit_id: UUID
    observed_at: datetime | None = None
    ingested_at: datetime

    class Config:
        from_attributes = True


class LatestPriceOut(BaseModel):
    price_date: date
    price_type: str
    price: float | None = None
    price_bid: float | None = None
    price_ask: float | None = None
    currency_code: str
    unit_code: str


class PriceQuery(BaseModel):
    commodity_slug: str | None = None
    variant_code: str | None = None
    market_code: str | None = None
    source_name: str | None = None
    price_type: str | None = None
    start: date | None = None
    end: date | None = None
    currency_code: str | None = None
    limit: int = 200
