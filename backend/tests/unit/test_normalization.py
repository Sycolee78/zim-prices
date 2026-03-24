from zim_prices_scrapers.normalization.contracts import normalize_contract
from zim_prices_scrapers.normalization.units import normalize_unit


def test_normalize_contract_maize_hre_usd():
    parts = normalize_contract("MAIZE/B/HRE/USD")
    assert parts.commodity_root == "maize"
    assert parts.variant_code == "B"
    assert parts.market_code == "HRE"
    assert parts.currency == "USD"


def test_normalize_unit_aliases():
    assert normalize_unit("kgs") == "kg"
    assert normalize_unit("Kgs") == "kg"
    assert normalize_unit("kg") == "kg"
    assert normalize_unit("L") == "l"
    assert normalize_unit("ltr") == "l"
