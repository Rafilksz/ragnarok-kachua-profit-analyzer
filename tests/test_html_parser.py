from src.html_parser import (
    is_exact_item_match,
    lowest_offer_price,
    parse_market_history,
    parse_trading_offers,
)


def test_parse_market_history_exact_item_match() -> None:
    html = """
    <ul>
      <li>Oridecon mínimo 0 máximo 150.000 médio 20.314 Vol 85507</li>
      <li>Minério de Oridecon mínimo 350 máximo 25.000 médio 3.328 Vol 2749</li>
    </ul>
    """

    history = parse_market_history(html, "Oridecon")

    assert history.has_history is True
    assert history.item_name == "Oridecon"
    assert history.minimum_price == 0
    assert history.maximum_price == 150000
    assert history.average_price == 20314
    assert history.volume == 85507


def test_parse_market_history_rejects_similar_item_name() -> None:
    html = """
    <ul>
      <li>Minério de Oridecon mínimo 350 máximo 25.000 médio 3.328 Vol 2749</li>
    </ul>
    """

    history = parse_market_history(html, "Oridecon")

    assert history.has_history is False


def test_exact_item_match_ignores_accents_but_not_words() -> None:
    assert is_exact_item_match("Máscara Azulada", "Mascara Azulada") is True
    assert is_exact_item_match("Minério de Oridecon", "Oridecon") is False


def test_parse_trading_offers_and_lowest_price() -> None:
    html = """
    <ul>
      <li>
        <h3 class="card_item_name__abc">Oridecon</h3>
        <p class="card_item_price__abc">1.500</p>
        <span>Nome do Comércio</span><span>Loja 1</span>
        <span>Vendedor</span><span>Alice</span>
        <span>Quantidade</span><span>10</span>
      </li>
      <li>
        <h3 class="card_item_name__abc">Oridecon</h3>
        <p class="card_item_price__abc">500</p>
        <span>Nome do Comércio</span><span>Loja 2</span>
        <span>Vendedor</span><span>Bob</span>
        <span>Quantidade</span><span>3</span>
      </li>
      <li>
        <h3 class="card_item_name__abc">Minério de Oridecon</h3>
        <p class="card_item_price__abc">100</p>
      </li>
    </ul>
    """

    offers = parse_trading_offers(html, "Oridecon", "SELL")

    assert len(offers) == 2
    assert lowest_offer_price(offers) == 500
