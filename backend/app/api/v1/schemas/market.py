from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel


class RegionOut(BaseModel):
    id: UUID
    name: str
    region_type: str
    country_code: str

    class Config:
        from_attributes = True


class MarketOut(BaseModel):
    id: UUID
    name: str
    market_code: str | None = None
    region_id: UUID

    class Config:
        from_attributes = True
