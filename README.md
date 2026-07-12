# Ragnarok Kachua Profit Analyzer

Aplicação para analisar se compensa abrir **Artefato Oval** no servidor **FREYA** do Ragnarok Online LATAM, usando estatística de drop, preço histórico de mercado e preços atuais de lojas de compra/venda.

## Objetivo

Criar uma aplicação que:

1. Receba uma lista de itens com:

   * nome do item;
   * quantidade recebida;
   * probabilidade de drop.

2. Consulte automaticamente o site oficial de mercado da GNJOY LATAM.

3. Verifique se o item já teve histórico de comércio.

4. Caso tenha histórico, colete:

   * preço mínimo histórico;
   * preço médio histórico;
   * preço máximo histórico;
   * volume negociado.

5. Consulte as lojas atuais para descobrir:

   * se há lojas comprando o item;
   * maior preço de compra disponível;
   * opcionalmente, se há lojas vendendo o item;
   * menor preço de venda disponível.

6. Calcule o valor esperado de cada item com base na chance de drop.

7. Calcule a partir de quantos Artefatos Ovais a abertura começa a compensar.

8. Compare o custo em BRL com o retorno esperado em zeny e BRL.

9. Informe se vale a pena abrir os Artefatos Ovais ou se é melhor não abrir.

---

## Contexto do jogo

Cada **Artefato Oval** custa:

```text
1.000 Joy Coin
```

Cada Artefato Oval aberto retorna:

```text
1 item aleatório da lista de drops
+
1 Cupom da Kachua garantido
```

O item **Cupom da Kachua** sempre vem junto:

```text
Cupom da Kachua    1    100,0000%
```

Portanto, o Cupom da Kachua deve ser tratado como item determinístico, e não como parte da roleta principal.

---

## Pacotes de Joy Coin

A aplicação deve considerar os seguintes pacotes oficiais:

| Joy Coin |    BRL |
| -------: | -----: |
|    2.025 |   4,00 |
|    4.000 |   7,90 |
|   10.100 |  19,90 |
|   20.300 |  39,90 |
|   50.900 |  99,90 |
|  102.000 | 199,90 |
|  184.000 | 359,90 |
|  384.000 | 749,90 |
|  513.000 | 999,90 |

Cada Artefato Oval custa:

```text
1.000 Joy Coin
```

A aplicação deve calcular:

```text
custo_por_joy_coin_brl = valor_brl / quantidade_joy_coin
custo_por_artefato_brl = custo_por_joy_coin_brl * 1000
```

Também deve permitir escolher:

```text
- melhor pacote;
- pacote específico;
- média ponderada;
- pacote manual informado pelo usuário.
```

Para a primeira versão, usar o pacote de melhor custo-benefício, ou seja, o menor valor de BRL por Joy Coin.

---

## Lista inicial de drops

A aplicação deve aceitar uma lista em texto, CSV, TSV ou planilha.

Formato esperado:

```text
Nome    Quantidade    Probabilidade
Coroa de Belzebu [1]    1    0,0250%
Botas Decadentes [1]    1    0,0250%
Envelope de Alto Refino    1    0,0500%
Martelo de Refino Vivatus    1    0,2250%
Âmago Dimensional    1    0,2250%
Martelo de Refino OSAD    1    0,3500%
Familiar de Combate    1    0,3500%
Drainiliar de Combate    1    0,3500%
Caixa de Armas Primordiais    1    0,3500%
Caixa de Elmos da Fé    1    0,4000%
Caixa de Elmos da Fé II    1    0,4000%
Comunicador Avançado    1    1,0000%
Gálea Guerreira de Cinzas [1]    1    1,0000%
Gálea Afiada de Cinzas [1]    1    1,0000%
Gálea Mágica de Cinzas [1]    1    1,0000%
Gálea Lutadora de Cinzas [1]    1    1,0000%
Caixa de Fascículos Selecionáveis    1    1,0000%
Cubo Sombrio do Chilique    1    1,5000%
Cubo Sombrio de Gateira    1    1,5000%
Caderno Perfeito    1    1,5000%
Cubo Sombrio de Es    1    2,0000%
Cubo Sombrio Kunoichi    1    2,0000%
Cubo Sombrio Shinobi    1    2,0000%
Cubo Sombrio de Expurgar    1    2,0000%
Cubo Sombrio Lunar    1    2,5000%
Cubo Sombrio Solar    1    2,5000%
Bênção do Ferreiro (3)    1    3,0000%
Encantador Sombrio    3    3,0000%
Vale-Encanto    1    3,0000%
Cubo Sombrio de Classe    1    3,0000%
Caixa de Martelos Sombrios    1    3,0000%
[Evento] Manual & Chiclete    1    4,7500%
[Evento] Poção Menor de Mana    2    4,7500%
[Evento] Poção Média de Vida    2    4,7500%
Estimulante    2    4,7500%
[Limitado] Amuleto de Siegfried    3    4,7500%
[Evento] Bênção de Tyr    5    7,0000%
Maleta de Produtos Químicos    2    7,0000%
Porta Moedas    2    7,0000%
Embalagem de Fragmentos    2    7,0000%
Poção de Ouro    3    7,0000%
Cupom da Kachua    1    100,0000%
```

---

## Regras de parsing da lista de itens

A lista será lida linha por linha.

Cada linha possui:

```text
Nome do item    Quantidade    Probabilidade
```

Como alguns nomes possuem espaços, colchetes e parênteses, o parser deve separar os campos da direita para a esquerda.

Exemplo:

```text
Gálea Afiada de Cinzas [1]    1    1,0000%
```

Separação correta:

```text
probabilidade = 1,0000%
quantidade = 1
nome_original = Gálea Afiada de Cinzas [1]
```

Depois disso, gerar um nome limpo para busca:

```text
nome_original = Gálea Afiada de Cinzas [1]
nome_busca = Gálea Afiada de Cinzas
```

---

## Limpeza do nome do item

Antes de montar a URL de busca, remover:

```text
[1]
[2]
[3]
[qualquer coisa dentro de colchetes]

(1)
(2)
(3)
(qualquer coisa dentro de parênteses)
```

A regra deve remover tudo que estiver entre:

```text
[ e ]
```

e tudo que estiver entre:

```text
( e )
```

Exemplos:

| Nome original                   | Nome para busca        |
| ------------------------------- | ---------------------- |
| Coroa de Belzebu [1]            | Coroa de Belzebu       |
| Botas Decadentes [1]            | Botas Decadentes       |
| Bênção do Ferreiro (3)          | Bênção do Ferreiro     |
| Gálea Afiada de Cinzas [1]      | Gálea Afiada de Cinzas |
| [Evento] Poção Menor de Mana    | Poção Menor de Mana    |
| [Limitado] Amuleto de Siegfried | Amuleto de Siegfried   |

Observação importante:

```text
[Evento] e [Limitado] também devem ser removidos.
```

Depois da remoção, aplicar:

```text
strip()
```

para remover espaços extras no começo e no fim.

---

## Encoding da URL

Nunca montar manualmente o texto da URL substituindo espaço por `+`.

Usar a biblioteca padrão do Python:

```python
from urllib.parse import quote_plus
```

Exemplo:

```python
from urllib.parse import quote_plus

nome = "Gálea Afiada de Cinzas"
nome_encoded = quote_plus(nome)

print(nome_encoded)
```

Resultado esperado:

```text
G%C3%A1lea+Afiada+de+Cinzas
```

Exemplos:

| Nome                     | Encoded                           |
| ------------------------ | --------------------------------- |
| Poção de Ouro            | Po%C3%A7%C3%A3o+de+Ouro           |
| Gálea Mágica de Cinzas   | G%C3%A1lea+M%C3%A1gica+de+Cinzas  |
| Bênção do Ferreiro       | B%C3%AAn%C3%A7%C3%A3o+do+Ferreiro |
| Âmago Dimensional        | %C3%82mago+Dimensional            |
| Cubo Sombrio do Chilique | Cubo+Sombrio+do+Chilique          |

---

## URLs do site

Servidor padrão:

```text
FREYA
```

### Consulta de histórico de preço

Usar primeiro a página de histórico:

```text
https://ro.gnjoylatam.com/pt/intro/shop-search/market-price?serverType=FREYA&period=ALL&searchWord={ITEM_ENCODED}
```

Exemplo:

```text
https://ro.gnjoylatam.com/pt/intro/shop-search/market-price?serverType=FREYA&period=ALL&searchWord=Po%C3%A7%C3%A3o+de+Ouro
```

Essa página serve para descobrir se o item já teve comércio.

Se não retornar resultado relevante para o item, marcar:

```text
sem_historico = True
item_comercializado = False
```

Se retornar resultado, coletar:

```text
preco_minimo_historico
preco_maximo_historico
preco_medio_historico
volume_negociado
```

### Consulta de lojas

Depois de confirmar que o item tem histórico, consultar a página de lojas.

Para lojas comprando o item:

```text
https://ro.gnjoylatam.com/pt/intro/shop-search/trading?storeType=BUY&serverType=FREYA&searchWord={ITEM_ENCODED}
```

Exemplo:

```text
https://ro.gnjoylatam.com/pt/intro/shop-search/trading?storeType=BUY&serverType=FREYA&searchWord=G%C3%A1lea+M%C3%A1gica+de+Cinzas
```

Para lojas vendendo o item:

```text
https://ro.gnjoylatam.com/pt/intro/shop-search/trading?storeType=SELL&serverType=FREYA&searchWord={ITEM_ENCODED}
```

---

## Interpretação de BUY e SELL

A aplicação deve tratar os tipos assim:

### `storeType=BUY`

Representa lojas que estão **comprando** o item.

Esse é o preço usado quando o jogador quer vender o item rapidamente para uma lojinha compradora.

Nesse caso, o preço mais importante é:

```text
maior_preco_compra
```

Porque, se existem várias lojas comprando, devemos vender para quem paga mais.

### `storeType=SELL`

Representa lojas que estão **vendendo** o item.

Esse dado é útil para saber o preço de mercado anunciado.

Nesse caso, o preço mais importante é:

```text
menor_preco_venda
```

Porque, se existem várias lojas vendendo, o menor preço é o concorrente mais barato.

### Regra principal para esta aplicação

Para calcular retorno conservador e venda rápida:

```text
usar storeType=BUY
usar maior_preco_compra
```

Para estimar preço de venda criando uma loja própria:

```text
usar storeType=SELL
usar menor_preco_venda
```

Na primeira versão do app, implementar obrigatoriamente:

```text
BUY -> maior_preco_compra
```

Depois implementar opcionalmente:

```text
SELL -> menor_preco_venda
```

---

## Correspondência exata do item

A busca do site pode retornar itens parecidos.

Exemplo: buscar por `Oridecon` pode retornar:

```text
Oridecon
Minério de Oridecon
Oridecon Perfeito
Flecha de Oridecon
```

Portanto, a aplicação não pode pegar o primeiro resultado automaticamente.

Ela deve:

1. limpar o nome original;
2. buscar no site;
3. coletar todos os resultados;
4. comparar o nome retornado pelo site com o nome limpo;
5. usar apenas resultado com correspondência exata.

Comparação sugerida:

```python
def normalize_for_compare(text: str) -> str:
    return " ".join(text.casefold().split())


def is_exact_item_match(site_name: str, searched_name: str) -> bool:
    return normalize_for_compare(site_name) == normalize_for_compare(searched_name)
```

---

## Bibliotecas recomendadas

Primeira versão:

```text
Python 3.12+
httpx
beautifulsoup4
lxml
pandas
streamlit
openpyxl
pydantic
pytest
```

Instalação:

```bash
python -m venv .venv
.venv\Scripts\activate

pip install httpx beautifulsoup4 lxml pandas streamlit openpyxl pydantic pytest
```

Se o site passar a depender de JavaScript:

```bash
pip install playwright
playwright install chromium
```

Mas a primeira tentativa deve ser com:

```text
httpx + BeautifulSoup
```

---

## Estrutura sugerida do projeto

```text
ragnarok-kachua-profit-analyzer/
│
├── README.md
├── requirements.txt
├── app.py
│
├── data/
│   ├── drops.txt
│   ├── joycoin_packages.csv
│   └── results.xlsx
│
├── src/
│   ├── __init__.py
│   │
│   ├── config.py
│   ├── models.py
│   ├── parser.py
│   ├── url_builder.py
│   ├── gnjoy_client.py
│   ├── html_parser.py
│   ├── market_analyzer.py
│   ├── profit_calculator.py
│   └── exporter.py
│
└── tests/
    ├── test_parser.py
    ├── test_url_builder.py
    └── test_profit_calculator.py
```

---

## Arquivo `requirements.txt`

Criar:

```text
httpx
beautifulsoup4
lxml
pandas
streamlit
openpyxl
pydantic
pytest
```

---

## Modelos de dados

Criar em:

```text
src/models.py
```

Modelos sugeridos:

```python
from dataclasses import dataclass
from decimal import Decimal


@dataclass
class DropItem:
    original_name: str
    search_name: str
    quantity: int
    probability_percent: Decimal
    is_guaranteed: bool = False


@dataclass
class MarketHistory:
    item_name: str
    minimum_price: int | None
    average_price: int | None
    maximum_price: int | None
    volume: int | None
    has_history: bool


@dataclass
class TradingOffer:
    item_name: str
    store_name: str | None
    character_name: str | None
    quantity: int
    price: int
    store_type: str


@dataclass
class ItemAnalysis:
    original_name: str
    search_name: str
    quantity_per_drop: int
    probability_percent: Decimal

    has_history: bool
    historical_minimum: int | None
    historical_average: int | None
    historical_maximum: int | None
    historical_volume: int | None

    has_buy_shop: bool
    highest_buy_price: int | None

    has_sell_shop: bool
    lowest_sell_price: int | None

    selected_price_zeny: int | None
    expected_value_zeny_per_box: Decimal
    expected_value_brl_per_box: Decimal
```

---

## Parser da lista de drops

Criar em:

```text
src/parser.py
```

Responsabilidades:

1. Ler texto bruto.
2. Ignorar cabeçalho.
3. Separar cada linha da direita para esquerda.
4. Extrair:

   * nome;
   * quantidade;
   * probabilidade.
5. Remover colchetes e parênteses do nome para gerar `search_name`.
6. Converter porcentagem brasileira para `Decimal`.

Exemplo de função:

```python
import re
from decimal import Decimal
from src.models import DropItem


def clean_item_name(name: str) -> str:
    name = re.sub(r"\[[^\]]*\]", "", name)
    name = re.sub(r"\([^\)]*\)", "", name)
    name = " ".join(name.split())
    return name.strip()


def parse_probability(value: str) -> Decimal:
    value = value.strip().replace("%", "").replace(".", "").replace(",", ".")
    return Decimal(value)


def parse_drop_line(line: str) -> DropItem | None:
    line = line.strip()

    if not line:
        return None

    if line.lower().startswith("nome"):
        return None

    parts = line.rsplit(maxsplit=2)

    if len(parts) != 3:
        raise ValueError(f"Linha inválida: {line}")

    original_name = parts[0].strip()
    quantity = int(parts[1])
    probability = parse_probability(parts[2])

    search_name = clean_item_name(original_name)

    return DropItem(
        original_name=original_name,
        search_name=search_name,
        quantity=quantity,
        probability_percent=probability,
        is_guaranteed=probability == Decimal("100.0000") or probability == Decimal("100"),
    )
```

---

## Montagem das URLs

Criar em:

```text
src/url_builder.py
```

Usar `quote_plus`.

```python
from urllib.parse import quote_plus


BASE_URL = "https://ro.gnjoylatam.com/pt/intro/shop-search"


def build_market_price_url(item_name: str, server: str = "FREYA", period: str = "ALL") -> str:
    encoded = quote_plus(item_name)

    return (
        f"{BASE_URL}/market-price"
        f"?serverType={server}"
        f"&period={period}"
        f"&searchWord={encoded}"
    )


def build_trading_url(item_name: str, store_type: str, server: str = "FREYA") -> str:
    encoded = quote_plus(item_name)

    return (
        f"{BASE_URL}/trading"
        f"?storeType={store_type}"
        f"&serverType={server}"
        f"&searchWord={encoded}"
    )
```

Testes obrigatórios:

```python
def test_encode_pocao_de_ouro():
    url = build_market_price_url("Poção de Ouro")
    assert "Po%C3%A7%C3%A3o+de+Ouro" in url


def test_encode_galea_magica():
    url = build_trading_url("Gálea Mágica de Cinzas", "BUY")
    assert "G%C3%A1lea+M%C3%A1gica+de+Cinzas" in url
```

---

## Cliente HTTP

Criar em:

```text
src/gnjoy_client.py
```

Responsabilidades:

1. Fazer requisições HTTP.
2. Usar headers de navegador.
3. Aplicar timeout.
4. Respeitar intervalo entre buscas.
5. Retornar HTML.

Exemplo:

```python
import time
import httpx


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 Chrome/120 Safari/537.36"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
}


class GnjoyClient:
    def __init__(self, delay_seconds: float = 1.0):
        self.delay_seconds = delay_seconds
        self.client = httpx.Client(
            headers=HEADERS,
            timeout=30,
            follow_redirects=True,
        )

    def get_html(self, url: str) -> str:
        time.sleep(self.delay_seconds)

        response = self.client.get(url)
        response.raise_for_status()

        return response.text

    def close(self) -> None:
        self.client.close()
```

---

## Parser do HTML

Criar em:

```text
src/html_parser.py
```

Responsabilidades:

1. Receber HTML da página `market-price`.
2. Extrair resultados de histórico.
3. Receber HTML da página `trading`.
4. Extrair ofertas de lojas.
5. Filtrar por nome exato.

Como a estrutura HTML pode mudar, implementar os parsers de forma isolada para facilitar manutenção.

Funções esperadas:

```python
def parse_market_history(html: str, searched_name: str) -> MarketHistory:
    ...
```

```python
def parse_trading_offers(html: str, searched_name: str, store_type: str) -> list[TradingOffer]:
    ...
```

Regras:

```text
- Se não encontrar item exato, retornar has_history=False.
- Se encontrar item exato, extrair mínimo, média, máximo e volume.
- Em trading BUY, retornar todas as ofertas de compra.
- Em trading SELL, retornar todas as ofertas de venda.
```

Converter preços como:

```text
1,000,000,000
1.000.000.000
1000000000
```

para:

```python
1000000000
```

Função sugerida:

```python
def parse_zeny(value: str) -> int:
    cleaned = (
        value.replace(",", "")
        .replace(".", "")
        .replace("zeny", "")
        .replace("Zeny", "")
        .strip()
    )

    return int(cleaned)
```

---

## Fluxo de análise por item

Criar em:

```text
src/market_analyzer.py
```

Fluxo:

```text
Para cada item da lista:

1. Gerar URL de histórico.
2. Baixar HTML de histórico.
3. Procurar item exato.
4. Se não tiver histórico:
   - marcar item como sem comércio;
   - não consultar trading;
   - selected_price_zeny = None.
5. Se tiver histórico:
   - salvar mínimo, médio, máximo e volume;
   - gerar URL trading BUY;
   - buscar lojas comprando;
   - pegar maior preço de compra;
   - gerar URL trading SELL opcionalmente;
   - buscar lojas vendendo;
   - pegar menor preço de venda.
6. Escolher preço usado no cálculo.
```

Regra de preço para primeira versão:

```text
Se existir maior_preco_compra:
    selected_price_zeny = maior_preco_compra
Senão:
    selected_price_zeny = None
```

Regra alternativa futura:

```text
Se modo = "venda_rapida":
    usar maior_preco_compra
Se modo = "venda_em_loja":
    usar menor_preco_venda
Se modo = "historico_medio":
    usar preco_medio_historico
```

---

## Estatística de drop

Para cada item aleatório:

```text
valor_esperado_item_por_artefato =
    quantidade_do_item
    × preço_do_item_em_zeny
    × probabilidade_decimal
```

Onde:

```text
probabilidade_decimal = probabilidade_percentual / 100
```

Exemplo:

```text
Item: Poção de Ouro
Quantidade: 3
Chance: 7,0000%
Preço unitário: 1.000.000 zeny

Valor esperado:
3 × 1.000.000 × 0,07 = 210.000 zeny por Artefato Oval
```

Para o Cupom da Kachua:

```text
valor_esperado_cupom =
    quantidade
    × preço_do_cupom
    × 1
```

Como ele é 100%, ele entra como item garantido.

---

## Valor esperado total

```text
EV_total_zeny_por_artefato =
    soma(valor_esperado_de_todos_os_itens)
```

Converter para BRL:

```text
EV_total_brl_por_artefato =
    EV_total_zeny_por_artefato / zeny_por_real
```

Lucro esperado por Artefato Oval:

```text
lucro_esperado_brl =
    EV_total_brl_por_artefato - custo_por_artefato_brl
```

ROI:

```text
roi_percentual =
    lucro_esperado_brl / custo_por_artefato_brl × 100
```

---

## Conversão zeny para real

A aplicação precisa saber quanto vale o zeny em reais.

Ela pode calcular isso a partir de uma referência manual.

Exemplo:

```text
100.000.000 zeny = R$ 10,00
```

Então:

```text
zeny_por_real = 100.000.000 / 10
zeny_por_real = 10.000.000
```

Conversão:

```text
valor_brl = valor_zeny / zeny_por_real
```

Na interface, permitir o usuário informar:

```text
Quantidade de zeny
Valor em reais
```

Exemplo:

```text
Zeny: 100000000
BRL: 10.00
```

---

## Cálculo de 1 até X Artefatos Ovais

A aplicação deve permitir simular:

```text
1 até X Artefatos Ovais
```

Exemplo:

```text
X = 1000
```

Para cada quantidade:

```text
custo_total_brl = quantidade_artefatos × custo_por_artefato_brl
retorno_esperado_zeny = quantidade_artefatos × EV_total_zeny_por_artefato
retorno_esperado_brl = retorno_esperado_zeny / zeny_por_real
lucro_esperado_brl = retorno_esperado_brl - custo_total_brl
```

A aplicação deve identificar:

```text
primeira_quantidade_lucrativa
```

Ou seja:

```text
menor número de Artefatos Ovais onde lucro_esperado_brl > 0
```

Se nunca ficar lucrativo até X:

```text
Não compensa abrir até X Artefatos Ovais com os preços atuais.
```

---

## Atenção sobre estatística

Como as chances de drop de itens raros são muito baixas, a aplicação deve diferenciar:

```text
valor esperado estatístico
```

de:

```text
risco real de abrir poucos Artefatos
```

Exemplo:

```text
Um item com 0,0250% de chance pode aumentar muito o valor esperado,
mas a chance real de obtê-lo em poucos Artefatos é extremamente baixa.
```

A aplicação deve calcular também a chance acumulada de obter pelo menos 1 unidade de cada item raro:

```text
chance_acumulada = 1 - (1 - p) ^ n
```

Onde:

```text
p = chance decimal do item
n = quantidade de Artefatos Ovais abertos
```

Exemplo:

```text
Chance de 0,0250% em 1000 Artefatos:

p = 0,00025
n = 1000

chance = 1 - (1 - 0,00025)^1000
chance ≈ 22,12%
```

Isso ajuda a mostrar que o lucro esperado pode depender de sorte extrema.

---

## Métricas finais do relatório

A aplicação deve gerar uma tabela por item com:

```text
Nome original
Nome usado na busca
Quantidade por drop
Chance %
Tem histórico?
Histórico mínimo
Histórico médio
Histórico máximo
Volume histórico
Tem loja comprando?
Maior preço de compra
Tem loja vendendo?
Menor preço de venda
Preço usado no cálculo
Valor esperado em zeny por Artefato
Valor esperado em BRL por Artefato
Observações
```

Também gerar resumo geral:

```text
Custo do Artefato Oval em Joy Coin
Custo do Artefato Oval em BRL
Taxa zeny por real
EV total em zeny por Artefato
EV total em BRL por Artefato
Lucro esperado por Artefato
ROI esperado
Quantidade mínima para lucro esperado
Itens sem histórico
Itens sem loja comprando
Itens com baixo volume histórico
Itens que mais contribuem para o EV
```

---

## Classificação de risco dos itens

Adicionar alertas:

```text
SEM_HISTORICO
SEM_LOJA_COMPRANDO
SEM_LOJA_VENDENDO
BAIXO_VOLUME
ITEM_RARO_COM_ALTO_IMPACTO
PRECO_USANDO_HISTORICO
PRECO_USANDO_BUY
PRECO_INDISPONIVEL
```

Regras sugeridas:

```text
Se volume histórico < 5:
    BAIXO_VOLUME

Se chance < 0,1% e preço usado é alto:
    ITEM_RARO_COM_ALTO_IMPACTO

Se não tem loja comprando:
    SEM_LOJA_COMPRANDO

Se não tem preço nenhum:
    PRECO_INDISPONIVEL
```

---

## Interface Streamlit

Criar em:

```text
app.py
```

A interface deve ter:

```text
1. Campo para colar lista de drops.
2. Campo para informar servidor. Padrão: FREYA.
3. Campo para informar preço do zeny em reais.
4. Seleção do pacote de Joy Coin.
5. Campo para informar quantidade máxima de Artefatos para simular.
6. Botão "Analisar".
7. Tabela detalhada por item.
8. Resumo financeiro.
9. Gráfico de lucro esperado de 1 até X Artefatos.
10. Exportação para Excel.
```

---

## Exportação

Criar em:

```text
src/exporter.py
```

Exportar arquivo Excel com abas:

```text
Resumo
Itens
Simulação
Itens sem preço
Configuração
```

Usar:

```text
pandas
openpyxl
```

---

## Cuidados com o site

A aplicação deve evitar excesso de requisições.

Usar delay entre consultas:

```text
1 segundo ou mais
```

Não consultar em loop infinito.

Salvar cache local dos resultados para não repetir busca do mesmo item toda hora.

Sugestão de cache:

```text
data/cache/
```

Cada item pode ter cache por data/hora.

Exemplo:

```text
data/cache/FREYA/Pocao_de_Ouro_market_price.html
data/cache/FREYA/Pocao_de_Ouro_trading_BUY.html
data/cache/FREYA/Pocao_de_Ouro_trading_SELL.html
```

---

## Ordem de implementação sugerida para o Codex

### Etapa 1 — Criar estrutura do projeto

Criar pastas:

```text
src/
tests/
data/
```

Criar arquivos:

```text
requirements.txt
app.py
src/models.py
src/parser.py
src/url_builder.py
src/gnjoy_client.py
src/html_parser.py
src/market_analyzer.py
src/profit_calculator.py
src/exporter.py
```

### Etapa 2 — Implementar parser da lista

Implementar:

```python
clean_item_name()
parse_probability()
parse_drop_line()
parse_drop_text()
```

Testar com:

```text
Gálea Afiada de Cinzas [1]    1    1,0000%
Bênção do Ferreiro (3)    1    3,0000%
[Evento] Poção Menor de Mana    2    4,7500%
```

Resultados esperados:

```text
Gálea Afiada de Cinzas
Bênção do Ferreiro
Poção Menor de Mana
```

### Etapa 3 — Implementar montagem das URLs

Implementar:

```python
build_market_price_url()
build_trading_url()
```

Validar encoding de acentos:

```text
Poção de Ouro
Gálea Mágica de Cinzas
Bênção do Ferreiro
Âmago Dimensional
```

### Etapa 4 — Baixar HTML

Implementar:

```python
GnjoyClient.get_html()
```

Testar com:

```text
Poção de Ouro
Botas Decadentes
Gálea Mágica de Cinzas
```

Salvar HTML bruto em:

```text
data/debug/
```

### Etapa 5 — Implementar parser de histórico

Implementar:

```python
parse_market_history()
```

Ele deve retornar:

```text
has_history
minimum_price
average_price
maximum_price
volume
```

### Etapa 6 — Implementar parser de trading

Implementar:

```python
parse_trading_offers()
```

Para `BUY`:

```text
retornar lojas comprando
calcular maior preço de compra
```

Para `SELL`:

```text
retornar lojas vendendo
calcular menor preço de venda
```

### Etapa 7 — Implementar análise completa por item

Implementar:

```python
analyze_item()
analyze_items()
```

### Etapa 8 — Implementar cálculo financeiro

Implementar:

```python
calculate_best_joycoin_package()
calculate_box_cost_brl()
calculate_expected_value()
calculate_profit_simulation()
calculate_accumulated_drop_chance()
```

### Etapa 9 — Criar interface Streamlit

Implementar:

```bash
streamlit run app.py
```

### Etapa 10 — Exportar Excel

Implementar botão:

```text
Exportar relatório .xlsx
```

---

## Fórmulas principais

### Probabilidade decimal

```text
p = probabilidade_percentual / 100
```

### Valor esperado de um item

```text
EV_item =
    quantidade
    × preço_unitário_zeny
    × p
```

### Valor esperado total

```text
EV_total =
    soma(EV_item)
```

### Custo do Artefato em BRL

```text
custo_artefato_brl =
    1000 × valor_brl_do_pacote / joycoins_do_pacote
```

### Conversão zeny para BRL

```text
valor_brl =
    valor_zeny / zeny_por_real
```

### Lucro esperado por Artefato

```text
lucro_brl =
    EV_total_brl - custo_artefato_brl
```

### ROI

```text
ROI =
    lucro_brl / custo_artefato_brl × 100
```

### Chance acumulada de dropar pelo menos 1

```text
chance_acumulada =
    1 - (1 - p) ^ quantidade_artefatos
```

---

## Exemplo de resultado esperado

```text
Resumo

Servidor: FREYA
Custo do Artefato Oval: 1.000 Joy Coin
Pacote usado: 513.000 Joy Coin por R$ 999,90
Custo por Artefato: R$ 1,9491
Taxa zeny/real: 10.000.000 zeny por R$ 1,00

Valor esperado por Artefato:
EV zeny: 15.500.000
EV BRL: R$ 1,55

Lucro esperado:
R$ -0,3991 por Artefato

Conclusão:
Não compensa abrir com os preços atuais.
```

Outro exemplo:

```text
Valor esperado por Artefato:
EV zeny: 25.000.000
EV BRL: R$ 2,50

Custo por Artefato:
R$ 1,9491

Lucro esperado:
R$ 0,5509 por Artefato

Conclusão:
Compensa estatisticamente, mas verificar risco dos itens raros.
```

---

## Observações importantes

1. Não usar apenas preço médio histórico para decidir lucro.
2. Priorizar preço real de compra atual, usando `storeType=BUY`.
3. Se não houver loja comprando, o item pode ter valor teórico, mas baixa liquidez.
4. Itens com volume histórico baixo devem receber alerta.
5. Itens raros podem distorcer o valor esperado.
6. Sempre mostrar uma conclusão conservadora.
7. A aplicação deve deixar claro que resultado estatístico não garante lucro em poucas aberturas.

---

## Comando para rodar

Instalar dependências:

```bash
pip install -r requirements.txt
```

Rodar aplicação:

```bash
streamlit run app.py
```

Rodar testes:

```bash
pytest
```

---

## Prompt sugerido para usar no Codex

Use este prompt no Codex dentro do VSCode:

```text
Implemente este projeto seguindo o README.md.

Comece criando a estrutura de pastas e arquivos.

Primeiro implemente:
1. src/models.py
2. src/parser.py
3. src/url_builder.py
4. tests/test_parser.py
5. tests/test_url_builder.py

Depois rode os testes e corrija os erros.

Não implemente Streamlit ainda.
A primeira entrega deve ser apenas parser, URL builder e testes.
```

Depois da primeira etapa:

```text
Agora implemente o cliente HTTP em src/gnjoy_client.py e crie uma função de debug para baixar o HTML de market-price e trading de um item, salvando em data/debug.
Use delay entre requisições e headers de navegador.
```

Depois:

```text
Agora implemente src/html_parser.py para extrair o histórico de preço e as ofertas de trading a partir dos HTMLs salvos em data/debug.
Use BeautifulSoup.
Crie funções isoladas e testes com fixtures HTML.
```

Depois:

```text
Agora implemente a análise completa em src/market_analyzer.py, combinando parser, URL builder, cliente HTTP e parser HTML.
A análise deve retornar uma lista de ItemAnalysis.
```

Depois:

```text
Agora implemente src/profit_calculator.py com cálculo de valor esperado, custo por Artefato Oval, conversão zeny/BRL, ROI, simulação de 1 até X Artefatos e chance acumulada de drop.
```

Depois:

```text
Agora crie a interface app.py em Streamlit para colar a lista de drops, configurar servidor, zeny por real, pacote de Joy Coin, quantidade máxima de Artefatos e exibir o relatório final.
```

---

## Definição de pronto da primeira versão

A primeira versão estará pronta quando:

```text
- O usuário conseguir colar a lista de drops.
- A aplicação limpar corretamente nomes com [1], [Evento], [Limitado] e (3).
- A aplicação montar URLs corretamente com acentos.
- A aplicação consultar market-price.
- A aplicação consultar trading BUY.
- A aplicação calcular maior preço de compra.
- A aplicação calcular valor esperado por item.
- A aplicação calcular valor esperado total.
- A aplicação comparar com custo do Artefato Oval.
- A aplicação informar se compensa ou não abrir.
- A aplicação exportar Excel.
```
