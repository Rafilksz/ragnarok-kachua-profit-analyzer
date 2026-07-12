from decimal import Decimal

from src.models import DropItem
from src.profit_calculator import (
    calculate_accumulated_drop_chance,
    calculate_best_joycoin_package,
    calculate_buy_fast_price,
    calculate_expected_value_zeny,
    calculate_zeny_per_real,
    summarize_profit,
)


def test_calculate_best_joycoin_package_uses_lowest_brl_per_joy_coin() -> None:
    package = calculate_best_joycoin_package()

    assert package.joy_coin == 513000
    assert package.brl == Decimal("999.90")


def test_calculate_zeny_per_real() -> None:
    assert calculate_zeny_per_real(100_000_000, Decimal("10.00")) == Decimal(
        "10000000"
    )


def test_calculate_expected_value_for_drop_item() -> None:
    item = DropItem(
        original_name="Poção de Ouro",
        search_name="Poção de Ouro",
        quantity=3,
        probability_percent=Decimal("7.0000"),
    )

    assert calculate_expected_value_zeny(item, 1_000_000) == Decimal("210000.000000")


def test_calculate_accumulated_drop_chance_for_rare_item() -> None:
    chance = calculate_accumulated_drop_chance(Decimal("0.0250"), 1000)

    assert chance.quantize(Decimal("0.01")) == Decimal("22.12")


def test_calculate_buy_fast_price_uses_two_percent_discount() -> None:
    assert calculate_buy_fast_price(210_000_000) == 205_800_000
    assert calculate_buy_fast_price(None) is None


def test_summarize_profit_identifies_profitable_ev() -> None:
    item = DropItem(
        original_name="Cupom da Kachua",
        search_name="Cupom da Kachua",
        quantity=1,
        probability_percent=Decimal("100.0000"),
        is_guaranteed=True,
    )

    expected_value = calculate_expected_value_zeny(item, 25_000_000)
    priced_item = type(
        "PricedItem",
        (),
        {"expected_value_zeny_per_box": expected_value},
    )()

    summary, simulation = summarize_profit(
        priced_items=[priced_item],
        artifact_cost_brl=Decimal("1.9491"),
        zeny_per_real=Decimal("10000000"),
        max_artifacts=10,
    )

    assert summary.expected_profit_brl_per_box > 0
    assert summary.first_profitable_quantity == 1
    assert len(simulation) == 10
