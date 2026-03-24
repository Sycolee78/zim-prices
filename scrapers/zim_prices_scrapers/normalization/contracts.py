from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ContractParts:
    raw: str
    commodity_root: str | None
    variant_code: str | None
    market_code: str | None
    currency: str | None


def normalize_contract(contract: str) -> ContractParts:
    """Split a ZMX contract string like "MAIZE/B/HRE/USD" into components.

    This is intentionally simple and stateless; persistent mapping to
    canonical commodity/market IDs is done in the backend using this
    parsed representation.
    """

    parts = [p.strip() for p in contract.split("/") if p.strip()]

    commodity_root = parts[0].lower() if parts else None
    variant_code = parts[1] if len(parts) > 1 else None
    market_code = parts[2] if len(parts) > 2 else None
    currency = parts[-1] if parts and parts[-1] in {"USD", "ZWG", "ZWL", "ZiG"} else None

    return ContractParts(
        raw=contract,
        commodity_root=commodity_root,
        variant_code=variant_code,
        market_code=market_code,
        currency=currency,
    )
