from decimal import Decimal

import pytest

from src.parser import (
    clean_item_name,
    is_non_tradeable_event_item,
    parse_drop_line,
    parse_drop_text,
    parse_probability,
)


@pytest.mark.parametrize(
    ("original_name", "expected_search_name"),
    [
        ("Coroa de Belzebu [1]", "Coroa de Belzebu"),
        ("Botas Decadentes [1]", "Botas Decadentes"),
        ("Bênção do Ferreiro (3)", "Bênção do Ferreiro"),
        ("Gálea Afiada de Cinzas [1]", "Gálea Afiada de Cinzas"),
        ("[Evento] Poção Menor de Mana", "Poção Menor de Mana"),
        ("[Limitado] Amuleto de Siegfried", "Amuleto de Siegfried"),
    ],
)
def test_clean_item_name(original_name: str, expected_search_name: str) -> None:
    assert clean_item_name(original_name) == expected_search_name


def test_parse_drop_line_complete() -> None:
    item = parse_drop_line("Gálea Afiada de Cinzas [1]    1    1,0000%")

    assert item is not None
    assert item.original_name == "Gálea Afiada de Cinzas [1]"
    assert item.search_name == "Gálea Afiada de Cinzas"
    assert item.quantity == 1
    assert item.probability_percent == Decimal("1.0000")
    assert item.is_guaranteed is False


def test_parse_drop_line_marks_kachua_coupon_as_guaranteed() -> None:
    item = parse_drop_line("Cupom da Kachua    1    100,0000%")

    assert item is not None
    assert item.original_name == "Cupom da Kachua"
    assert item.search_name == "Cupom da Kachua"
    assert item.quantity == 1
    assert item.probability_percent == Decimal("100.0000")
    assert item.is_guaranteed is True


@pytest.mark.parametrize(
    ("raw_probability", "expected"),
    [
        ("0,0250%", Decimal("0.0250")),
        ("1,0000%", Decimal("1.0000")),
        ("7,0000%", Decimal("7.0000")),
        ("100,0000%", Decimal("100.0000")),
    ],
)
def test_parse_probability(raw_probability: str, expected: Decimal) -> None:
    assert parse_probability(raw_probability) == expected


def test_parse_drop_text_ignores_header_and_blank_lines() -> None:
    items = parse_drop_text(
        """
        Nome    Quantidade    Probabilidade
        Gálea Afiada de Cinzas [1]    1    1,0000%

        [Evento] Poção Menor de Mana    2    4,7500%
        """
    )

    assert [item.search_name for item in items] == [
        "Gálea Afiada de Cinzas",
        "Poção Menor de Mana",
    ]


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("[Evento] Manual & Chiclete", True),
        ("[Limitado] Amuleto de Siegfried", True),
        ("Poção de Ouro", False),
    ],
)
def test_is_non_tradeable_event_item(name: str, expected: bool) -> None:
    assert is_non_tradeable_event_item(name) is expected
