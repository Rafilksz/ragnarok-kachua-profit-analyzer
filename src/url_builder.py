from __future__ import annotations

from urllib.parse import quote_plus


BASE_URL = "https://ro.gnjoylatam.com/pt/intro/shop-search"


def build_market_price_url(
    item_name: str,
    server: str = "FREYA",
    period: str = "ALL",
) -> str:
    encoded_item_name = quote_plus(item_name)

    return (
        f"{BASE_URL}/market-price"
        f"?serverType={server}"
        f"&period={period}"
        f"&searchWord={encoded_item_name}"
    )


def build_trading_url(
    item_name: str,
    store_type: str,
    server: str = "FREYA",
) -> str:
    encoded_item_name = quote_plus(item_name)

    return (
        f"{BASE_URL}/trading"
        f"?storeType={store_type}"
        f"&serverType={server}"
        f"&searchWord={encoded_item_name}"
    )
