from __future__ import annotations

import re
import unicodedata

from bs4 import BeautifulSoup, Tag

from src.models import MarketHistory, TradingOffer


def normalize_for_compare(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    without_accents = "".join(
        character for character in normalized if not unicodedata.combining(character)
    )
    return " ".join(without_accents.casefold().split())


def is_exact_item_match(site_name: str, searched_name: str) -> bool:
    return normalize_for_compare(site_name) == normalize_for_compare(searched_name)


def parse_zeny(value: str) -> int:
    cleaned = (
        value.replace(",", "")
        .replace(".", "")
        .replace("zeny", "")
        .replace("Zeny", "")
        .strip()
    )
    numbers = re.findall(r"\d+", cleaned)
    return int("".join(numbers)) if numbers else 0


def parse_market_history(html: str, searched_name: str) -> MarketHistory:
    soup = BeautifulSoup(html, "lxml")

    for item_text in _iter_market_result_texts(soup):
        match = re.match(
            r"^(?P<name>.+?)\s+minimo\s+(?P<min>[\d.,]+)\s+maximo\s+"
            r"(?P<max>[\d.,]+)\s+medio\s+(?P<avg>[\d.,]+)\s+Vol\s+"
            r"(?P<volume>[\d.,]+)",
            _strip_accents_for_labels(item_text),
            flags=re.IGNORECASE,
        )

        if match is None:
            continue

        item_name = match.group("name").strip()

        if not is_exact_item_match(item_name, searched_name):
            continue

        return MarketHistory(
            item_name=item_name,
            minimum_price=parse_zeny(match.group("min")),
            average_price=parse_zeny(match.group("avg")),
            maximum_price=parse_zeny(match.group("max")),
            volume=parse_zeny(match.group("volume")),
            has_history=True,
        )

    return MarketHistory(
        item_name=searched_name,
        minimum_price=None,
        average_price=None,
        maximum_price=None,
        volume=None,
        has_history=False,
    )


def parse_trading_offers(
    html: str,
    searched_name: str,
    store_type: str,
) -> list[TradingOffer]:
    soup = BeautifulSoup(html, "lxml")
    offers: list[TradingOffer] = []

    for card in _iter_trading_cards(soup):
        item_name = _find_text_by_class_part(card, "card_item_name")

        if item_name is None or not is_exact_item_match(item_name, searched_name):
            continue

        price_text = _find_text_by_class_part(card, "card_item_price") or "0"
        card_text = " ".join(card.get_text(" ", strip=True).split())

        offers.append(
            TradingOffer(
                item_name=item_name,
                store_name=_extract_labeled_value(card_text, "Nome do Comercio")
                or _extract_labeled_value(card_text, "Nome do Comércio"),
                character_name=_extract_labeled_value(card_text, "Vendedor"),
                quantity=_extract_int_after_label(card_text, "Quantidade"),
                price=parse_zeny(price_text),
                store_type=store_type,
            )
        )

    return offers


def lowest_offer_price(offers: list[TradingOffer]) -> int | None:
    if not offers:
        return None

    return min(offer.price for offer in offers)


def highest_offer_price(offers: list[TradingOffer]) -> int | None:
    if not offers:
        return None

    return max(offer.price for offer in offers)


def _iter_market_result_texts(soup: BeautifulSoup) -> list[str]:
    result_texts: list[str] = []

    for li in soup.find_all("li"):
        text = " ".join(li.get_text(" ", strip=True).split())

        if "mínimo" in text and "máximo" in text and "médio" in text:
            result_texts.append(text)

    return result_texts


def _iter_trading_cards(soup: BeautifulSoup) -> list[Tag]:
    cards: list[Tag] = []

    for item_name_node in soup.find_all(class_=_class_contains("card_item_name")):
        card = item_name_node.find_parent("li")

        if isinstance(card, Tag):
            cards.append(card)

    return cards


def _find_text_by_class_part(card: Tag, class_part: str) -> str | None:
    node = card.find(class_=_class_contains(class_part))

    if node is None:
        return None

    return " ".join(node.get_text(" ", strip=True).split())


def _class_contains(class_part: str):
    def matcher(class_value: str | list[str] | None) -> bool:
        if class_value is None:
            return False

        if isinstance(class_value, list):
            return any(class_part in value for value in class_value)

        return class_part in class_value

    return matcher


def _extract_labeled_value(text: str, label: str) -> str | None:
    pattern = rf"{re.escape(label)}\s+(.+?)(?:\s+Vendedor|\s+Tipo|\s+Quantidade|$)"
    match = re.search(pattern, text)
    return match.group(1).strip() if match else None


def _extract_int_after_label(text: str, label: str) -> int:
    match = re.search(rf"{re.escape(label)}\s+(\d+)", text)
    return int(match.group(1)) if match else 0


def _strip_accents_for_labels(text: str) -> str:
    return (
        text.replace("mínimo", "minimo")
        .replace("máximo", "maximo")
        .replace("médio", "medio")
    )
