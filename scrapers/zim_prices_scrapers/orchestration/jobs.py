from __future__ import annotations

import json
import os
from datetime import date
from typing import Literal

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from zim_prices_scrapers.sources.zmx import scrape_zmx_market_watch


def _get_database_url() -> str:
    # Reuse the same env var as the backend where possible
    return os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://zim_prices:zim_prices@localhost:5434/zim_prices",
    )


def _get_source_id(db: Session) -> object:
    """Ensure a `Source` row for ZMX exists and return its id.

    Imports the backend model lazily to avoid hard coupling at import time.
    """

    from app.db.models.source import Source  # type: ignore

    stmt = select(Source).where(Source.name == "zmx")
    obj = db.execute(stmt).scalar_one_or_none()
    if obj:
        return obj.id

    src = Source(name="zmx", base_url="https://system.zmx.co.zw/", terms_url=None)
    db.add(src)
    db.flush()
    return src.id


def run_zmx_daily(write_to_db: bool = True) -> None:
    """Run the daily ZMX scrape.

    Phase 2.1: if `write_to_db` is True, map normalized records into the
    PostgreSQL schema via `upsert_zmx_observation`. Otherwise, print JSON
    lines to stdout for inspection.
    """

    records = scrape_zmx_market_watch()

    if not write_to_db:
        for rec in records:
            print(json.dumps(rec, default=str))
        return

    # Lazy import to avoid circular deps when scrapers is used standalone
    from app.services.ingestion_zmx import upsert_zmx_observation  # type: ignore

    engine = create_engine(_get_database_url(), future=True)
    today = date.today()

    with Session(engine) as db:
        source_id = _get_source_id(db)

        for rec in records:
            upsert_zmx_observation(
                db,
                obs=rec,
                source_id=source_id,
                price_date=today,
                price_type="last",
            )

        db.commit()


def main(task: Literal["run_zmx_daily"] = "run_zmx_daily") -> None:
    if task == "run_zmx_daily":
        run_zmx_daily(write_to_db=True)
    else:
        raise SystemExit(f"Unknown task: {task}")


if __name__ == "__main__":  # pragma: no cover
    main()
