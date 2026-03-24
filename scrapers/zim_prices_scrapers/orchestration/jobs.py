from __future__ import annotations

import json
from typing import Literal

from zim_prices_scrapers.sources.zmx import scrape_zmx_market_watch


def run_zmx_daily() -> None:
    """Run the daily ZMX scrape.

    For Phase 2, this just prints normalized JSON lines to stdout so
    you can inspect the structure and wire it into the backend later.
    In Phase 3+, this will:
      - persist raw artifacts
      - upsert into the PostgreSQL schema via SQLAlchemy
    """

    records = scrape_zmx_market_watch()
    for rec in records:
        print(json.dumps(rec, default=str))


def main(task: Literal["run_zmx_daily"] = "run_zmx_daily") -> None:
    if task == "run_zmx_daily":
        run_zmx_daily()
    else:
        raise SystemExit(f"Unknown task: {task}")


if __name__ == "__main__":  # pragma: no cover
    main()
