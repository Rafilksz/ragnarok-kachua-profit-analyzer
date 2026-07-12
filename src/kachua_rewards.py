from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from src.models import DropItem


@dataclass(frozen=True)
class KachuaReward:
    coupon_cost: int
    item_name: str


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
