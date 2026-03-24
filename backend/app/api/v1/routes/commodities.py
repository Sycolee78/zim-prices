from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models.commodity import Commodity
from app.api.v1.schemas.commodity import CommodityOut

router = APIRouter(prefix="/commodities", tags=["commodities"])


@router.get("", response_model=List[CommodityOut])
def list_commodities(db: Session = Depends(get_db)) -> list[CommodityOut]:
    query = db.query(Commodity).order_by(Commodity.slug.asc())
    return query.all()
