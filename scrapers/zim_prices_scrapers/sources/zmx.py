from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List

import pandas as pd
import requests

from zim_prices_scrapers.normalization.contracts import normalize_contract
from zim_prices_scrapers.normalization.units import normalize_unit


ZMX_URL = "https://system.zmx.co.zw/zmxwebpage/ATSCommo.aspx"


@dataclass
class ZmxObservation:
    contract: str
    unit: str | None
    vwa: float | None
    last_price: float | None
    best_bid_price: float | None
    best_ask_price: float | None
    traded_volume: float | None
    turnover: float | None


def fetch_zmx_tables(timeout_s: int = 30) -> List[pd.DataFrame]:
    """Fetch all HTML tables from the ZMX Market Watch page.

    In practice this should yield at least the Market Watch and
    Recent Orders tables. This function does no interpretation; it
    just returns raw DataFrames for downstream normalization.
    """

    resp = requests.get(ZMX_URL, timeout=timeout_s)
    resp.raise_for_status()
    return pd.read_html(resp.text)


def extract_market_watch(df: pd.DataFrame) -> list[ZmxObservation]:
    """Best-effort extraction of observations from a Market Watch table.

    This is deliberately tolerant: column names may change, so we
    try to map by approximate labels where possible.
    """

    cols = {c.lower().strip(): c for c in df.columns}

    def col(name: str) -> Any:
        for key, orig in cols.items():
            if name in key:
                return df[orig]
        raise KeyError(f"No column matching {name!r} in ZMX table columns: {list(df.columns)}")

    observations: list[ZmxObservation] = []

    contract_col = col("contract") if any("contract" in c.lower() for c in df.columns) else col("commodity")

    unit_col = None
    for k, orig in cols.items():
        if "unit" in k:
            unit_col = df[orig]
            break

    vwa_col = None
    for k, orig in cols.items():
        if "vwa" in k or "vwap" in k:
            vwa_col = df[orig]
            break

    last_col = None
    for k, orig in cols.items():
        if "last" in k:
            last_col = df[orig]
            break

    bid_col = None
    for k, orig in cols.items():
        if "bid" in k and "vol" not in k:
            bid_col = df[orig]
            break

    ask_col = None
    for k, orig in cols.items():
        if "ask" in k and "vol" not in k:
            ask_col = df[orig]
            break

    vol_col = None
    for k, orig in cols.items():
        if "traded" in k or "volume" in k:
            vol_col = df[orig]
            break

    turnover_col = None
    for k, orig in cols.items():
        if "turnover" in k:
            turnover_col = df[orig]
            break

    for idx in range(len(df)):
        contract = str(contract_col.iloc[idx]).strip()
        if not contract or contract.lower() == "nan":
            continue

        unit_val = None
        if unit_col is not None:
            unit_val = normalize_unit(str(unit_col.iloc[idx]))

        def safe_float(series) -> float | None:
            if series is None:
                return None
            try:
                val = str(series.iloc[idx]).replace(",", "").strip()
                if not val:
                    return None
                return float(val)
            except Exception:
                return None

        observations.append(
            ZmxObservation(
                contract=contract,
                unit=unit_val,
                vwa=safe_float(vwa_col),
                last_price=safe_float(last_col),
                best_bid_price=safe_float(bid_col),
                best_ask_price=safe_float(ask_col),
                traded_volume=safe_float(vol_col),
                turnover=safe_float(turnover_col),
            )
        )

    return observations


def scrape_zmx_market_watch(timeout_s: int = 30) -> list[dict[str, object]]:
    """High-level ZMX scraper returning normalized dicts.

    This does not write to the database yet; it prepares the shape
    that the backend ingestion service can later map into
    `commodity`, `market`, and `price_observation` rows.
    """

    tables = fetch_zmx_tables(timeout_s=timeout_s)
    if not tables:
        return []

    # Heuristically treat the first table as Market Watch for now.
    market_watch_df = tables[0]
    obs = extract_market_watch(market_watch_df)

    normalized: list[dict[str, object]] = []

    for o in obs:
        parts = normalize_contract(o.contract)
        normalized.append(
            {
                "contract_raw": o.contract,
                "commodity_root": parts.commodity_root,
                "variant_code": parts.variant_code,
                "market_code": parts.market_code,
                "currency_code": parts.currency,
                "unit": o.unit,
                "vwa": o.vwa,
                "last_price": o.last_price,
                "best_bid_price": o.best_bid_price,
                "best_ask_price": o.best_ask_price,
                "traded_volume": o.traded_volume,
                "turnover": o.turnover,
            }
        )

    return normalized
