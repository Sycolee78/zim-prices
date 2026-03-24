from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models.commodity import Commodity, CommodityVariant
from app.db.models.region_market import Market
from app.db.models.currency_unit import Currency, Unit
from app.db.models.price_observation import PriceObservation
from app.api.v1.schemas.price import PriceObservationOut, LatestPriceOut

router = APIRouter(prefix="/prices", tags=["prices"])


@router.get("", response_model=List[PriceObservationOut])
def list_prices(
    db: Session = Depends(get_db),
    commodity: str | None = Query(None, description="Commodity slug (e.g. maize)"),
    variant: str | None = Query(None, description="Variant code (e.g. B)"),
    market: str | None = Query(None, description="Market code (e.g. HRE)"),
    source: str | None = Query(None, description="Source name (e.g. zmx)"),
    price_type: str | None = Query(None),
    start: str | None = Query(None, description="Start date (YYYY-MM-DD)"),
    end: str | None = Query(None, description="End date (YYYY-MM-DD)"),
    limit: int = Query(200, ge=1, le=1000),
) -> list[PriceObservationOut]:
    """Raw price observations with flexible filters.

    This is intentionally low-level; the frontend will usually use the
    `/series` or `/latest` style endpoints, but this is useful for debugging
    and exports.
    """

    q = db.query(PriceObservation)

    if commodity:
        q = q.join(CommodityVariant, PriceObservation.commodity_variant_id == CommodityVariant.id)
        q = q.join(Commodity, CommodityVariant.commodity_id == Commodity.id)
        q = q.filter(Commodity.slug == commodity)

    if variant:
        if "CommodityVariant" not in str(q):
            q = q.join(CommodityVariant, PriceObservation.commodity_variant_id == CommodityVariant.id)
        q = q.filter(CommodityVariant.variant_code == variant)

    if market:
        q = q.join(Market, PriceObservation.market_id == Market.id)
        q = q.filter(Market.market_code == market)

    if price_type:
        q = q.filter(PriceObservation.price_type == price_type)

    if start:
        q = q.filter(PriceObservation.price_date >= start)
    if end:
        q = q.filter(PriceObservation.price_date <= end)

    q = q.order_by(PriceObservation.price_date.desc(), PriceObservation.ingested_at.desc())
    q = q.limit(limit)

    return q.all()


@router.get("/latest", response_model=LatestPriceOut)
def latest_price(
    db: Session = Depends(get_db),
    commodity: str = Query(..., description="Commodity slug (e.g. petrol_blend_e5)"),
    market: str | None = Query(None, description="Market code (e.g. ZW or HRE)"),
    price_type: str | None = Query(None, description="Price type (e.g. last, retail_cap)"),
) -> LatestPriceOut:
    """Latest observation for a commodity (+optional market).

    For now this is a simple MAX(price_date, ingested_at) query; later you
    can refine staleness rules and source preferences.
    """

    stmt = (
        select(PriceObservation, Currency.code, Unit.code)
        .join(CommodityVariant, PriceObservation.commodity_variant_id == CommodityVariant.id)
        .join(Commodity, CommodityVariant.commodity_id == Commodity.id)
        .join(Market, PriceObservation.market_id == Market.id)
        .join(Currency, PriceObservation.currency_id == Currency.id)
        .join(Unit, PriceObservation.unit_id == Unit.id)
        .where(Commodity.slug == commodity)
    )

    if market:
        stmt = stmt.where(Market.market_code == market)

    if price_type:
        stmt = stmt.where(PriceObservation.price_type == price_type)

    stmt = stmt.order_by(PriceObservation.price_date.desc(), PriceObservation.ingested_at.desc())
    stmt = stmt.limit(1)

    row = db.execute(stmt).first()
    if not row:
        raise HTTPException(status_code=404, detail="No price found for given filters")

    obs: PriceObservation = row[0]
    currency_code: str = row[1]
    unit_code: str = row[2]

    return LatestPriceOut(
        price_date=obs.price_date,
        price_type=obs.price_type,
        price=float(obs.price) if obs.price is not None else None,
        price_bid=float(obs.price_bid) if obs.price_bid is not None else None,
        price_ask=float(obs.price_ask) if obs.price_ask is not None else None,
        currency_code=currency_code,
        unit_code=unit_code,
    )
