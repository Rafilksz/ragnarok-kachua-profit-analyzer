from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from src.models import DropItem


@dataclass(frozen=True)
class KachuaReward:
    coupon_cost: int
    item_name: str


@dataclass(frozen=True)
class KachuaRewardQuote:
    reward: KachuaReward
    unit_price_zeny: int | None

    @property
    def zeny_per_coupon(self) -> Decimal:
        if self.unit_price_zeny is None:
            return Decimal("0")

        return Decimal(self.unit_price_zeny) / Decimal(self.reward.coupon_cost)


@dataclass(frozen=True)
class KachuaRedemption:
    reward: KachuaReward
    quantity: int
    unit_price_zeny: int
    spent_coupons: int

    @property
    def total_zeny(self) -> Decimal:
        return Decimal(self.quantity) * Decimal(self.unit_price_zeny)

    @property
    def zeny_per_coupon(self) -> Decimal:
        return Decimal(self.unit_price_zeny) / Decimal(self.reward.coupon_cost)


DEFAULT_KACHUA_REWARDS = [
    KachuaReward(1500, "Auréola Celeste"),
    KachuaReward(800, "CD Antiquado"),
    KachuaReward(800, "Pena de Águia"),
    KachuaReward(800, "Mascara Azulada"),
    KachuaReward(800, "Tiara de Runas"),
    KachuaReward(250, "Bênção de Thor"),
    KachuaReward(250, "Orelhas Anciãs"),
    KachuaReward(200, "Cabelos da Himmelmez"),
    KachuaReward(200, "Caixa de Sombrio de Curar"),
    KachuaReward(200, "Caixa de Sombrio de Esconderijo"),
    KachuaReward(200, "Caixa de Sombrio de Furtividade"),
    KachuaReward(1500, "Cubo de Refino de Memorável"),
    KachuaReward(900, "Cubo de Refino do Torneio"),
    KachuaReward(40, "Bênção do Ferreiro"),
    KachuaReward(40, "Martelo de Refino Sombrio"),
]


def is_kachua_coupon(item: DropItem) -> bool:
    return item.search_name.casefold() == "cupom da kachua"


def calculate_coupon_count(items: list[DropItem], artifact_quantity: int) -> int:
    for item in items:
        if is_kachua_coupon(item):
            return item.quantity * artifact_quantity

    return artifact_quantity


def calculate_redeemable_quantity(coupon_count: int, coupon_cost: int) -> int:
    if coupon_cost <= 0:
        raise ValueError("coupon_cost must be greater than zero")

    return coupon_count // coupon_cost


def calculate_reward_total_zeny(
    coupon_count: int,
    coupon_cost: int,
    unit_price_zeny: int | None,
) -> Decimal:
    if unit_price_zeny is None:
        return Decimal("0")

    return Decimal(calculate_redeemable_quantity(coupon_count, coupon_cost)) * Decimal(
        unit_price_zeny
    )


def optimize_kachua_redemptions(
    coupon_count: int,
    quotes: list[KachuaRewardQuote],
) -> tuple[list[KachuaRedemption], int]:
    remaining_coupons = coupon_count
    redemptions: list[KachuaRedemption] = []

    available_quotes = [
        quote
        for quote in quotes
        if quote.unit_price_zeny is not None and quote.unit_price_zeny > 0
    ]

    while True:
        affordable_quotes = [
            quote
            for quote in available_quotes
            if quote.reward.coupon_cost <= remaining_coupons
        ]

        if not affordable_quotes:
            break

        best_quote = max(
            affordable_quotes,
            key=lambda quote: (
                quote.zeny_per_coupon,
                quote.unit_price_zeny or 0,
                -quote.reward.coupon_cost,
            ),
        )
        quantity = remaining_coupons // best_quote.reward.coupon_cost
        spent_coupons = quantity * best_quote.reward.coupon_cost

        redemptions.append(
            KachuaRedemption(
                reward=best_quote.reward,
                quantity=quantity,
                unit_price_zeny=best_quote.unit_price_zeny or 0,
                spent_coupons=spent_coupons,
            )
        )
        remaining_coupons -= spent_coupons

    return redemptions, remaining_coupons
