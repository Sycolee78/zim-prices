from __future__ import annotations

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.commodity import Commodity, CommodityVariant
from app.db.models.region_market import Region, Market
from app.db.models.currency_unit import Currency, Unit
from app.db.models.price_observation import PriceObservation


def _get_or_create_commodity(
    db: Session,
    commodity_root: str,
    category: str = "industry",
) -> Commodity:
    slug = commodity_root.lower()
    stmt = select(Commodity).where(Commodity.slug == slug)
    obj = db.execute(stmt).scalar_one_or_none()
    if obj:
        return obj

    obj = Commodity(slug=slug, name=commodity_root.upper(), category=category)
    db.add(obj)
    db.flush()
    return obj


def _get_or_create_variant(
    db: Session,
    commodity: Commodity,
    variant_code: str | None,
) -> CommodityVariant:
    code = variant_code or "default"
    stmt = select(CommodityVariant).where(
        CommodityVariant.commodity_id == commodity.id,
        CommodityVariant.variant_code == code,
    )
    obj = db.execute(stmt).scalar_one_or_none()
    if obj:
        return obj

    obj = CommodityVariant(commodity_id=commodity.id, variant_code=code)
    db.add(obj)
    db.flush()
    return obj


def _get_or_create_region_country(db: Session) -> Region:
    stmt = select(Region).where(Region.region_type == "country", Region.country_code == "ZW")
    obj = db.execute(stmt).scalar_one_or_none()
    if obj:
        return obj

    obj = Region(name="Zimbabwe", region_type="country", country_code="ZW")
    db.add(obj)
    db.flush()
    return obj


def _get_or_create_market(
    db: Session,
    market_code: str | None,
) -> Market:
    country = _get_or_create_region_country(db)
    code = market_code or "ZW"

    stmt = select(Market).where(Market.market_code == code)
    obj = db.execute(stmt).scalar_one_or_none()
    if obj:
        return obj

    name = {
        "ZW": "Zimbabwe (National)",
    }.get(code, code)

    obj = Market(region_id=country.id, name=name, market_code=code)
    db.add(obj)
    db.flush()
    return obj


def _get_or_create_currency(db: Session, code: str | None) -> Currency:
    c = (code or "USD").upper()
    stmt = select(Currency).where(Currency.code == c)
    obj = db.execute(stmt).scalar_one_or_none()
    if obj:
        return obj

    obj = Currency(code=c, name=c)
    db.add(obj)
    db.flush()
    return obj


def _get_or_create_unit(db: Session, code: str | None) -> Unit:
    u = (code or "kg").lower()
    stmt = select(Unit).where(Unit.code == u)
    obj = db.execute(stmt).scalar_one_or_none()
    if obj:
        return obj

    obj = Unit(code=u, name=u, dimension="other")
    db.add(obj)
    db.flush()
    return obj


def upsert_zmx_observation(
    db: Session,
    *,
    obs: dict,
    source_id,
    price_date: date,
    price_type: str = "last",
) -> PriceObservation:
    """Map a normalized ZMX record into `price_observation`.

    This is a minimal upsert that:
    - creates missing commodities / markets / currency / unit on the fly
    - writes a single `price_observation` record per call

    Idempotency at the DB level should be enforced later via a unique
    constraint matching the schema design and `ON CONFLICT` logic.
    """

    commodity_root = obs.get("commodity_root") or "unknown"
    variant_code = obs.get("variant_code")
    market_code = obs.get("market_code")
    currency_code = obs.get("currency_code")
    unit_code = obs.get("unit")

    commodity = _get_or_create_commodity(db, commodity_root)
    variant = _get_or_create_variant(db, commodity, variant_code)
    market = _get_or_create_market(db, market_code)
    currency = _get_or_create_currency(db, currency_code)
    unit = _get_or_create_unit(db, unit_code)

    price_val = obs.get("last_price") or obs.get("vwa")

    po = PriceObservation(
        commodity_variant_id=variant.id,
        market_id=market.id,
        source_id=source_id,
        scrape_run_id=None,
        price_date=price_date,
        price_type=price_type,
        price=price_val,
        price_bid=obs.get("best_bid_price"),
        price_ask=obs.get("best_ask_price"),
        volume=obs.get("traded_volume"),
        turnover=obs.get("turnover"),
        currency_id=currency.id,
        unit_id=unit.id,
        quality_flags=[],
        source_payload=obs,
    )
    db.add(po)
    # Caller is responsible for commit
    return po
