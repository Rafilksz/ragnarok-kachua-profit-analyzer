from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass
class DropItem:
    original_name: str
    search_name: str
    quantity: int
    probability_percent: Decimal
    is_guaranteed: bool = False


@dataclass
class MarketHistory:
    item_name: str
    minimum_price: int | None
    average_price: int | None
    maximum_price: int | None
    volume: int | None
    has_history: bool


@dataclass
class TradingOffer:
    item_name: str
    store_name: str | None
    character_name: str | None
    quantity: int
    price: int
    store_type: str


@dataclass
class ItemAnalysis:
    original_name: str
    search_name: str
    quantity_per_drop: int
    probability_percent: Decimal
    has_history: bool
    historical_minimum: int | None
    historical_average: int | None
    historical_maximum: int | None
    historical_volume: int | None
    has_buy_shop: bool
    highest_buy_price: int | None
    has_sell_shop: bool
    lowest_sell_price: int | None
    selected_price_zeny: int | None
    expected_value_zeny_per_box: Decimal
    expected_value_brl_per_box: Decimal
