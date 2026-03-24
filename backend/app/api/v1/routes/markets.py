from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models.region_market import Market
from app.api.v1.schemas.market import MarketOut

router = APIRouter(prefix="/markets", tags=["markets"])


@router.get("", response_model=List[MarketOut])
def list_markets(db: Session = Depends(get_db)) -> list[MarketOut]:
    query = db.query(Market).order_by(Market.name.asc())
    return query.all()
