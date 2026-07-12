from decimal import Decimal

from src.kachua_rewards import (
    KachuaReward,
    KachuaRewardQuote,
    calculate_coupon_count,
    calculate_redeemable_quantity,
    calculate_reward_total_zeny,
    is_kachua_coupon,
    optimize_kachua_redemptions,
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


def test_optimize_kachua_redemptions_spends_remaining_coupons() -> None:
    memorable_cube = KachuaReward(1500, "Cubo de Refino de Memorável")
    blacksmith_blessing = KachuaReward(40, "Bênção do Ferreiro")
    weak_reward = KachuaReward(250, "Item Fraco")

    redemptions, remaining_coupons = optimize_kachua_redemptions(
        2000,
        [
            KachuaRewardQuote(memorable_cube, 3_000_000_000),
            KachuaRewardQuote(blacksmith_blessing, 50_000_000),
            KachuaRewardQuote(weak_reward, 10_000_000),
        ],
    )

    assert redemptions[0].reward.item_name == "Cubo de Refino de Memorável"
    assert redemptions[0].quantity == 1
    assert redemptions[0].spent_coupons == 1500
    assert redemptions[1].reward.item_name == "Bênção do Ferreiro"
    assert redemptions[1].quantity == 12
    assert redemptions[1].spent_coupons == 480
    assert remaining_coupons == 20
