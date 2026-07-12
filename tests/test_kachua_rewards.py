from decimal import Decimal

from src.kachua_rewards import (
    calculate_coupon_count,
    calculate_redeemable_quantity,
    calculate_reward_total_zeny,
    is_kachua_coupon,
)
from src.models import DropItem


def test_is_kachua_coupon() -> None:
    item = DropItem(
        original_name="Cupom da Kachua",
        search_name="Cupom da Kachua",
        quantity=1,
        probability_percent=Decimal("100.0000"),
        is_guaranteed=True,
    )

    assert is_kachua_coupon(item) is True


def test_calculate_coupon_count_uses_one_coupon_per_artifact() -> None:
    items = [
        DropItem(
            original_name="Cupom da Kachua",
            search_name="Cupom da Kachua",
            quantity=1,
            probability_percent=Decimal("100.0000"),
            is_guaranteed=True,
        )
    ]

    assert calculate_coupon_count(items, 1000) == 1000


def test_calculate_redeemable_quantity() -> None:
    assert calculate_redeemable_quantity(1000, 40) == 25
    assert calculate_redeemable_quantity(1000, 1500) == 0


def test_calculate_reward_total_zeny() -> None:
    assert calculate_reward_total_zeny(1000, 40, 10_000_000) == Decimal("250000000")
    assert calculate_reward_total_zeny(1000, 40, None) == Decimal("0")
