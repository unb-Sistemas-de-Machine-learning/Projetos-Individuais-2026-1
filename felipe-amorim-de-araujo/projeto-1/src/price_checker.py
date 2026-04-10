import re
import time
import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass
from urllib.parse import quote_plus

TIMEOUT = 10
MAX_RETRIES = 2

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
})


@dataclass
class Offer:
    store: str
    title: str
    price: float
    url: str


def verify_price(book_title: str) -> list[Offer]:
    checkers = [
        _search_mercado_livre,
        _search_amazon,
        _search_estante_virtual,
    ]
    offers = []
    for checker in checkers:
        try:
            result = checker(book_title)
            if result:
                offers.append(result)
        except Exception:
            pass
    return offers


def _search_mercado_livre(title: str) -> Offer | None:
    url = "https://api.mercadolibre.com/sites/MLB/search"
    params = {"q": title, "category": "MLB1196", "limit": 1}
    resp = SESSION.get(url, params=params, timeout=TIMEOUT)
    resp.raise_for_status()
    results = resp.json().get("results", [])
    if not results:
        return None
    item = results[0]
    price = item.get("price")
    if not price:
        return None
    return Offer(
        store="Mercado Livre",
        title=item.get("title", title),
        price=float(price),
        url=item.get("permalink", ""),
    )


def _search_amazon(title: str) -> Offer | None:
    url = f"https://www.amazon.com.br/s?k={quote_plus(title)}&i=stripbooks"
    resp = _get_with_retry(url)
    if not resp:
        return None
    soup = BeautifulSoup(resp.text, "html.parser")

    price_tag = (
        soup.select_one("span.a-price .a-offscreen") or
        soup.select_one("[data-component-type='s-search-result'] span.a-price .a-offscreen")
    )
    if not price_tag:
        return None

    price = _parse_price(price_tag.get_text())
    if not price:
        return None

    title_tag = soup.select_one("span.a-size-medium.a-color-base.a-text-normal")
    found_title = title_tag.get_text(strip=True) if title_tag else title

    return Offer(store="Amazon", title=found_title, price=price, url=url)


def _search_estante_virtual(title: str) -> Offer | None:
    url = f"https://www.estantevirtual.com.br/busca?q={quote_plus(title)}"
    resp = _get_with_retry(url)
    if not resp:
        return None
    soup = BeautifulSoup(resp.text, "html.parser")

    price_tag = (
        soup.select_one("[itemprop='price']") or
        soup.select_one("[class*='preco']") or
        soup.select_one("[class*='price']")
    )
    if not price_tag:
        return None

    price = _parse_price(price_tag.get("content") or price_tag.get_text())
    if not price:
        return None

    title_tag = (
        soup.select_one("[itemprop='name']") or
        soup.select_one("[class*='titulo']") or
        soup.select_one("h2")
    )
    found_title = title_tag.get_text(strip=True) if title_tag else title

    return Offer(store="Estante Virtual", title=found_title, price=price, url=url)


def _get_with_retry(url: str) -> requests.Response | None:
    for attempt in range(MAX_RETRIES):
        try:
            resp = SESSION.get(url, timeout=TIMEOUT)
            if resp.status_code == 200:
                return resp
            if resp.status_code == 429:
                time.sleep(2 ** attempt)
        except requests.RequestException:
            if attempt < MAX_RETRIES - 1:
                time.sleep(1)
    return None


def _parse_price(text: str) -> float | None:
    text = text.replace("R$", "").replace("\xa0", "").strip()
    match = re.search(r"(\d{1,3}(?:[.,]\d{3})*[.,]\d{2})", text)
    if not match:
        return None
    value = match.group(1)
    if re.match(r"\d+\.\d{3},\d{2}", value):
        value = value.replace(".", "").replace(",", ".")
    elif re.match(r"\d+,\d{2}$", value):
        value = value.replace(",", ".")
    try:
        return float(value)
    except ValueError:
        return None
