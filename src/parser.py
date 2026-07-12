from __future__ import annotations

import re
from decimal import Decimal

from src.models import DropItem


_BRACKETED_TEXT_PATTERN = re.compile(r"\[[^\]]*\]")
_PARENTHESIZED_TEXT_PATTERN = re.compile(r"\([^\)]*\)")


def clean_item_name(name: str) -> str:
    name_without_brackets = _BRACKETED_TEXT_PATTERN.sub("", name)
    name_without_parentheses = _PARENTHESIZED_TEXT_PATTERN.sub("", name_without_brackets)
    return " ".join(name_without_parentheses.split()).strip()


def is_non_tradeable_event_item(name: str) -> bool:
    normalized = name.casefold()
    return "[evento]" in normalized or "[limitado]" in normalized


def parse_probability(value: str) -> Decimal:
    normalized = value.strip().replace("%", "").replace(",", ".")
    return Decimal(normalized)


def parse_drop_line(line: str) -> DropItem | None:
    line = line.strip()

    if not line:
        return None

    if line.casefold().startswith("nome"):
        return None

    parts = line.rsplit(maxsplit=2)

    if len(parts) != 3:
        raise ValueError(f"Linha invalida: {line}")

    original_name = parts[0].strip()
    quantity = int(parts[1])
    probability_percent = parse_probability(parts[2])
    search_name = clean_item_name(original_name)

    return DropItem(
        original_name=original_name,
        search_name=search_name,
        quantity=quantity,
        probability_percent=probability_percent,
        is_guaranteed=probability_percent == Decimal("100.0000")
        or probability_percent == Decimal("100"),
    )


def parse_drop_text(text: str) -> list[DropItem]:
    items: list[DropItem] = []

    for line in text.splitlines():
        item = parse_drop_line(line)

        if item is not None:
            items.append(item)

    return items
