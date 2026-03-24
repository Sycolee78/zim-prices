from __future__ import annotations


_UNIT_ALIASES = {
    "kgs": "kg",
    "Kgs": "kg",
    "kGs": "kg",
    "KG": "kg",
    "L": "l",
    "ltr": "l",
    "Ltr": "l",
}


def normalize_unit(unit: str | None) -> str | None:
    if unit is None:
        return None
    unit = unit.strip()
    if not unit:
        return None
    return _UNIT_ALIASES.get(unit, unit.lower())
