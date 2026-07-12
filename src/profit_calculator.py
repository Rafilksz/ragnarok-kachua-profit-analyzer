from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from src.models import DropItem


ARTIFACT_COST_JOY_COIN = Decimal("1000")


@dataclass(frozen=True)
class JoyCoinPackage:
    joy_coin: int
    brl: Decimal

    @property
    def brl_per_joy_coin(self) -> Decimal:
        return self.brl / Decimal(self.joy_coin)

    @property
    def artifact_cost_brl(self) -> Decimal:
        return self.brl_per_joy_coin * ARTIFACT_COST_JOY_COIN


@dataclass(frozen=True)
class PricedDropItem:
    item: DropItem
    unit_price_zeny: int
    expected_value_zeny_per_box: Decimal
    expected_value_brl_per_box: Decimal
    accumulated_chance_percent: Decimal


@dataclass(frozen=True)
class ProfitSummary:
    artifact_cost_brl: Decimal
    zeny_per_real: Decimal
    expected_value_zeny_per_box: Decimal
    expected_value_brl_per_box: Decimal
    expected_profit_brl_per_box: Decimal
    roi_percent: Decimal
    first_profitable_quantity: int | None


@dataclass(frozen=True)
class SimulationRow:
    artifact_quantity: int
    total_cost_brl: Decimal
    expected_return_zeny: Decimal
    expected_return_brl: Decimal
    expected_profit_brl: Decimal


DEFAULT_JOYCOIN_PACKAGES = [
    JoyCoinPackage(joy_coin=2025, brl=Decimal("4.00")),
    JoyCoinPackage(joy_coin=4000, brl=Decimal("7.90")),
    JoyCoinPackage(joy_coin=10100, brl=Decimal("19.90")),
    JoyCoinPackage(joy_coin=20300, brl=Decimal("39.90")),
    JoyCoinPackage(joy_coin=50900, brl=Decimal("99.90")),
    JoyCoinPackage(joy_coin=102000, brl=Decimal("199.90")),
    JoyCoinPackage(joy_coin=184000, brl=Decimal("359.90")),
    JoyCoinPackage(joy_coin=384000, brl=Decimal("749.90")),
    JoyCoinPackage(joy_coin=513000, brl=Decimal("999.90")),
]


def calculate_best_joycoin_package(
    packages: list[JoyCoinPackage] | None = None,
) -> JoyCoinPackage:
    available_packages = packages or DEFAULT_JOYCOIN_PACKAGES
    return min(available_packages, key=lambda package: package.brl_per_joy_coin)


def calculate_zeny_per_real(reference_zeny: int, reference_brl: Decimal) -> Decimal:
    if reference_zeny <= 0:
        raise ValueError("reference_zeny must be greater than zero")

    if reference_brl <= 0:
        raise ValueError("reference_brl must be greater than zero")

    return Decimal(reference_zeny) / reference_brl


def probability_to_rate(probability_percent: Decimal) -> Decimal:
    return probability_percent / Decimal("100")


def calculate_expected_value_zeny(item: DropItem, unit_price_zeny: int) -> Decimal:
    if unit_price_zeny <= 0:
        return Decimal("0")

    return (
        Decimal(item.quantity)
        * Decimal(unit_price_zeny)
        * probability_to_rate(item.probability_percent)
    )


def calculate_buy_fast_price(price: int | None) -> int | None:
    if price is None:
        return None

    return int(Decimal(price) * Decimal("0.98"))


def calculate_accumulated_drop_chance(
    probability_percent: Decimal,
    artifact_quantity: int,
) -> Decimal:
    if artifact_quantity <= 0:
        return Decimal("0")

    probability = probability_to_rate(probability_percent)

    if probability >= 1:
        return Decimal("100")

    chance = Decimal("1") - ((Decimal("1") - probability) ** artifact_quantity)
    return chance * Decimal("100")


def price_drop_items(
    items: list[DropItem],
    prices_by_search_name: dict[str, int],
    zeny_per_real: Decimal,
    artifact_quantity_for_chance: int,
) -> list[PricedDropItem]:
    priced_items: list[PricedDropItem] = []

    for item in items:
        unit_price = prices_by_search_name.get(item.search_name, 0)
        expected_value_zeny = calculate_expected_value_zeny(item, unit_price)
        expected_value_brl = expected_value_zeny / zeny_per_real

        priced_items.append(
            PricedDropItem(
                item=item,
                unit_price_zeny=unit_price,
                expected_value_zeny_per_box=expected_value_zeny,
                expected_value_brl_per_box=expected_value_brl,
                accumulated_chance_percent=calculate_accumulated_drop_chance(
                    item.probability_percent,
                    artifact_quantity_for_chance,
                ),
            )
        )

    return priced_items


def simulate_profit(
    max_artifacts: int,
    artifact_cost_brl: Decimal,
    expected_value_zeny_per_box: Decimal,
    zeny_per_real: Decimal,
) -> list[SimulationRow]:
    if max_artifacts <= 0:
        raise ValueError("max_artifacts must be greater than zero")

    rows: list[SimulationRow] = []

    for artifact_quantity in range(1, max_artifacts + 1):
        total_cost_brl = artifact_cost_brl * Decimal(artifact_quantity)
        expected_return_zeny = expected_value_zeny_per_box * Decimal(artifact_quantity)
        expected_return_brl = expected_return_zeny / zeny_per_real

        rows.append(
            SimulationRow(
                artifact_quantity=artifact_quantity,
                total_cost_brl=total_cost_brl,
                expected_return_zeny=expected_return_zeny,
                expected_return_brl=expected_return_brl,
                expected_profit_brl=expected_return_brl - total_cost_brl,
            )
        )

    return rows


def summarize_profit(
    priced_items: list[PricedDropItem],
    artifact_cost_brl: Decimal,
    zeny_per_real: Decimal,
    max_artifacts: int,
) -> tuple[ProfitSummary, list[SimulationRow]]:
    expected_value_zeny = sum(
        (item.expected_value_zeny_per_box for item in priced_items),
        Decimal("0"),
    )
    expected_value_brl = expected_value_zeny / zeny_per_real
    expected_profit_brl = expected_value_brl - artifact_cost_brl
    roi_percent = (
        (expected_profit_brl / artifact_cost_brl) * Decimal("100")
        if artifact_cost_brl > 0
        else Decimal("0")
    )

    simulation = simulate_profit(
        max_artifacts=max_artifacts,
        artifact_cost_brl=artifact_cost_brl,
        expected_value_zeny_per_box=expected_value_zeny,
        zeny_per_real=zeny_per_real,
    )
    first_profitable_quantity = next(
        (
            row.artifact_quantity
            for row in simulation
            if row.expected_profit_brl > Decimal("0")
        ),
        None,
    )

    return (
        ProfitSummary(
            artifact_cost_brl=artifact_cost_brl,
            zeny_per_real=zeny_per_real,
            expected_value_zeny_per_box=expected_value_zeny,
            expected_value_brl_per_box=expected_value_brl,
            expected_profit_brl_per_box=expected_profit_brl,
            roi_percent=roi_percent,
            first_profitable_quantity=first_profitable_quantity,
        ),
        simulation,
    )
