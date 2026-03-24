from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel


class CommodityVariantOut(BaseModel):
    id: UUID
    variant_code: str
    grade: str | None = None

    class Config:
        from_attributes = True


class CommodityOut(BaseModel):
    id: UUID
    slug: str
    name: str
    category: str

    class Config:
        from_attributes = True
