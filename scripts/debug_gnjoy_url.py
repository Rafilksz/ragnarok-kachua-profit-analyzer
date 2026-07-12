from __future__ import annotations

import argparse
import sys
from pathlib import Path

import httpx

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.html_parser import (  # noqa: E402
    lowest_offer_price,
    parse_market_history,
    parse_trading_offers,
)
from src.profit_calculator import calculate_buy_fast_price  # noqa: E402
from src.url_builder import build_market_price_url, build_trading_url  # noqa: E402


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 Chrome/120 Safari/537.36"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
}


def format_zeny(value: int | None) -> str:
    if value is None:
        return "None"

    return f"{value:,}".replace(",", ".")


def fetch(url: str) -> str:
    print(f"URL: {url}")
    response = httpx.get(
        url,
        headers=HEADERS,
        timeout=30,
        follow_redirects=True,
    )
    print(f"STATUS: {response.status_code}")
    print(f"FINAL URL: {response.url}")
    print(f"BYTES: {len(response.text.encode('utf-8'))}")
    response.raise_for_status()
    return response.text


def debug_market(item: str, server: str, print_full_html: bool) -> None:
    url = build_market_price_url(item, server=server)
    html = fetch(url)
    history = parse_market_history(html, item)

    print("\nMARKET PARSED")
    print(f"has_history: {history.has_history}")
    print(f"item_name: {history.item_name}")
    print(f"min: {format_zeny(history.minimum_price)}")
    print(f"avg: {format_zeny(history.average_price)}")
    print(f"max: {format_zeny(history.maximum_price)}")
    print(f"volume: {format_zeny(history.volume)}")

    if print_full_html:
        print("\nFULL HTML MARKET")
        print(html)


def debug_trading(
    item: str,
    server: str,
    store_type: str,
    print_full_html: bool,
) -> None:
    url = build_trading_url(item, store_type, server=server)
    html = fetch(url)
    offers = parse_trading_offers(html, item, store_type)
    offers_sorted = sorted(offers, key=lambda offer: offer.price)
    lowest_price = lowest_offer_price(offers)
    buy_fast_price = (
        calculate_buy_fast_price(lowest_price) if store_type.upper() == "BUY" else None
    )

    print("\nTRADING PARSED")
    print(f"store_type: {store_type}")
    print(f"offers: {len(offers)}")
    print(f"lowest_price: {format_zeny(lowest_price)}")
    print(f"buy_fast_price_minus_2_percent: {format_zeny(buy_fast_price)}")
    print(f"all_prices: {[offer.price for offer in offers]}")

    print("\nOFFERS SORTED BY PRICE")
    for index, offer in enumerate(offers_sorted, start=1):
        print(
            f"{index}. price={format_zeny(offer.price)} "
            f"qty={offer.quantity} "
            f"store={offer.store_name!r} "
            f"seller={offer.character_name!r} "
            f"item={offer.item_name!r}"
        )

    if print_full_html:
        print("\nFULL HTML TRADING")
        print(html)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Debug one GNJOY market/trading URL and print the full response.",
    )
    parser.add_argument(
        "--item",
        default="Envelope de Alto Refino",
        help="Item name to search.",
    )
    parser.add_argument("--server", default="FREYA")
    parser.add_argument(
        "--mode",
        choices=["market", "trading", "both"],
        default="trading",
    )
    parser.add_argument(
        "--store-type",
        choices=["BUY", "SELL"],
        default="BUY",
    )
    parser.add_argument(
        "--no-full-html",
        action="store_true",
        help="Do not print the full HTML response.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    print_full_html = not args.no_full_html

    if args.mode in {"market", "both"}:
        debug_market(args.item, args.server, print_full_html)

    if args.mode in {"trading", "both"}:
        debug_trading(args.item, args.server, args.store_type, print_full_html)


if __name__ == "__main__":
    main()
