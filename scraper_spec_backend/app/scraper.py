from typing import Optional, List, Dict, Tuple
from urllib.parse import quote_plus, urlparse, urljoin
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
def build_search_url(keyword: str, domain: str = "amazon.com") -> str:
    return f"https://www.{domain}/s?k={quote_plus(keyword.strip())}"

def clean_url(u: str) -> str:
    """Strip tracking params. Keep scheme, host, and path."""
    try:
        p = urlparse(u)
        return f"{p.scheme}://{p.netloc}{p.path}"
    except Exception:
        return u

def normalize_price(raw: Optional[str]) -> Optional[float]:
    """'$59.99' | '59,99 €' | 'AED 129.00' -> 59.99"""
    if not raw:
        return None
    s = raw.strip()
    keep = ''.join(ch for ch in s if ch.isdigit() or ch in ['.', ','])
    if not keep:
        return None
    if '.' in keep and ',' in keep:
        keep = keep.replace(',', '')
    elif ',' in keep and '.' not in keep:
        keep = keep.replace(',', '.')
    try:
        return float(keep)
    except Exception:
        return None

def normalize_rating(raw: Optional[str]) -> Optional[float]:
    """'4.5 out of 5 stars' -> 4.5"""
    if not raw:
        return None
    s = raw.strip().lower().replace('out of 5 stars', '').replace('out of 5', '')
    keep = ''.join(ch for ch in s if ch.isdigit() or ch == '.')
    try:
        return float(keep) if keep else None
    except Exception:
        return None

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

def load_html_with_browser(url: str, wait_css: str = "div.s-main-slot",
                           delay_range=(2.0, 4.0), timeout_sec: int = 45) -> str | None:
    lo, hi = delay_range
    time.sleep(random.uniform(lo, hi))

    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument(f"user-agent={USER_AGENT}")
    opts.add_argument("--window-size=1366,900")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option('useAutomationExtension', False)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=opts)

    html = None
    try:
        driver.get(url)
        end = time.time() + timeout_sec
        found = False
        while time.time() < end:
            try:
                if driver.find_elements(By.CSS_SELECTOR, wait_css):
                    found = True
                    break
            except Exception:
                pass
            time.sleep(0.4)

        driver.execute_script("window.scrollTo(0, 1200);")
        time.sleep(1.0)
        driver.execute_script("window.scrollTo(0, 2400);")
        time.sleep(0.8)

        html = driver.page_source if found else driver.page_source
    finally:
        driver.quit()
    return html

AMZ_HOST = "https://www.amazon.com"

def canonical_product_url(asin: str, host: str = AMZ_HOST) -> str:
    return f"{host}/dp/{asin}"

def is_sponsored(card) -> bool:
    badge = (card.select_one("span.s-sponsored-label-text") or
             card.select_one("span.puis-label-popover-default") or
             card.select_one("span[aria-label='Sponsored']"))
    return badge is not None

def parse_title_and_href(card, asin: str):
    a = None
    title = None
    selectors = [
        "h2 a.a-link-normal",
        "h2.a-size-mini a",
        "a.a-link-normal.s-link-style",
        "a.a-link-normal.s-underline-text",
        "div.s-title-instructions-style a",
        "a[href*='/dp/']",
    ]
    for selector in selectors:
        a = card.select_one(selector)
        if a:
            break
    if not a:
        return None, None

    title_text = []
    for child in a.children:
        if isinstance(child, str):
            text = child.strip()
            if text and not any(x in text.lower() for x in ['out of', 'stars', 'rating']):
                title_text.append(text)
        elif child.name == 'span':
            classes = child.get('class', [])
            if not any('review' in c.lower() or 'rating' in c.lower() for c in classes):
                text = child.get_text(strip=True)
                if text and not (text.startswith('(') and text.endswith(')')) and not text.replace(',','').replace('.','').replace('K','').replace('M','').isdigit():
                    title_text.append(text)
    title = ' '.join(title_text).strip()
    if not title:
        import re
        full_text = a.get_text(' ', strip=True)
        full_text = re.sub(r'\(\d+\.?\d*[KM]?\)', '', full_text)
        full_text = re.sub(r'\d+\.?\d*\s*out of\s*\d+\.?\d*\s*stars', '', full_text, flags=re.IGNORECASE)
        full_text = re.sub(r'\d{1,3}(,\d{3})*\s*(reviews?|ratings?)', '', full_text, flags=re.IGNORECASE)
        title = full_text.strip()
    if not title:
        return None, None

    href = a.get("href", "")
    if href.startswith("/"):
        href = urljoin(AMZ_HOST, href)
    if "/sspa/" in (href or "") or "/gp/slredirect/" in (href or ""):
        href = canonical_product_url(asin)
    return title, href

def parse_price(card):
    offscreen = card.select_one("span.a-price span.a-offscreen")
    if offscreen:
        text = offscreen.get_text(strip=True)
        if text:
            return text
    offscreen_any = card.find("span", class_="a-offscreen")
    if offscreen_any:
        text = offscreen_any.get_text(strip=True)
        if text and '$' in text:
            return text
    whole = card.select_one("span.a-price-whole")
    if whole:
        w = whole.get_text(strip=True).replace(",", "")
        frac = card.select_one("span.a-price-fraction")
        f = (frac.get_text(strip=True) if frac else "00")
        return f"${w}.{f}"
    price_spans = card.find_all("span", class_=lambda x: x and "price" in x.lower())
    for span in price_spans:
        text = span.get_text(strip=True)
        if text and '$' in text:
            return text
    all_spans = card.find_all("span")
    for span in all_spans:
        text = span.get_text(strip=True)
        if text and '$' in text and any(c.isdigit() for c in text):
            return text
    return None

def parse_rating(card):
    t = card.select_one("span[aria-label$='out of 5 stars']") or card.select_one("span.a-icon-alt")
    return t.get_text(strip=True) if t else None

def parse_image(card):
    img = card.select_one("img.s-image") or card.find("img")
    if not img:
        return None
    for k in ("src", "data-src", "data-image-src", "srcset"):
        v = img.get(k)
        if v:
            if k == "srcset":
                v = v.split()[0]
            return v
    return None

def parse_search_page(html: str):
    soup = BeautifulSoup(html, "lxml")
    root = soup.select_one("div.s-main-slot") or soup
    cards = root.select("div[data-asin][data-component-type='s-search-result']")
    items = []
    for card in cards:
        asin = (card.get("data-asin") or "").strip()
        if not asin:
            continue
        if is_sponsored(card):
            continue
        title, href = parse_title_and_href(card, asin)
        if not title or not href:
            continue
        price_raw  = parse_price(card)
        rating_raw = parse_rating(card)
        image_url  = parse_image(card)
        items.append({
            "asin": asin,
            "title": title,
            "price": normalize_price(price_raw),
            "rating": normalize_rating(rating_raw),
            "product_url": href,
            "image_url": image_url,
        })
    nxt = soup.select_one("a.s-pagination-next:not(.s-pagination-disabled)")
    next_url = urljoin(AMZ_HOST, nxt["href"]) if nxt and nxt.has_attr("href") else None
    return items, next_url

def scrape_via_browser(
    keyword: str,
    domain: str = "amazon.com",
    max_pages: int = 2,
    delay: Tuple[float, float] = (2.5, 5.0)
) -> List[Dict]:
    url = build_search_url(keyword, domain=domain)
    all_items: List[Dict] = []
    page_no = 0
    while url and page_no < max_pages:
        page_no += 1
        html = load_html_with_browser(url, delay_range=delay)
        if not html:
            break
        page_items, next_url = parse_search_page(html)
        all_items.extend(page_items)
        url = next_url
    dedup = {it["asin"]: it for it in all_items if it.get("asin")}
    return list(dedup.values())

def scrape_by_url(
    search_url: str,
    max_pages: int = 1,
    delay: Tuple[float, float] = (2.5, 5.0)
) -> List[Dict]:
    url = search_url
    all_items: List[Dict] = []
    page_no = 0
    while url and page_no < max_pages:
        page_no += 1
        html = load_html_with_browser(url, delay_range=delay)
        if not html:
            break
        page_items, next_url = parse_search_page(html)
        all_items.extend(page_items)
        url = next_url
    dedup = {it["product_url"]: it for it in all_items if it.get("product_url")}
    return list(dedup.values())
