from src.url_builder import build_market_price_url, build_trading_url


def test_build_market_price_url_for_pocao_de_ouro() -> None:
    url = build_market_price_url("Poção de Ouro")

    assert (
        url
        == "https://ro.gnjoylatam.com/pt/intro/shop-search/market-price"
        "?serverType=FREYA&period=ALL&searchWord=Po%C3%A7%C3%A3o+de+Ouro"
    )


def test_build_trading_url_for_galea_magica_buy() -> None:
    url = build_trading_url("Gálea Mágica de Cinzas", "BUY")

    assert (
        url
        == "https://ro.gnjoylatam.com/pt/intro/shop-search/trading"
        "?storeType=BUY&serverType=FREYA"
        "&searchWord=G%C3%A1lea+M%C3%A1gica+de+Cinzas"
    )


def test_build_trading_url_for_sell() -> None:
    url = build_trading_url("Cubo Sombrio do Chilique", "SELL")

    assert "storeType=SELL" in url
    assert "searchWord=Cubo+Sombrio+do+Chilique" in url


def test_build_urls_encode_accents_and_cedilla() -> None:
    assert "B%C3%AAn%C3%A7%C3%A3o+do+Ferreiro" in build_market_price_url(
        "Bênção do Ferreiro"
    )
    assert "%C3%82mago+Dimensional" in build_market_price_url("Âmago Dimensional")


def test_build_urls_convert_spaces_to_plus() -> None:
    url = build_trading_url("Poção de Ouro", "BUY")

    assert "Po%C3%A7%C3%A3o+de+Ouro" in url
