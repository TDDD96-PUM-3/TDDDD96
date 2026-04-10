"""
universal_scraper.py
────────────────────
A site-agnostic scraper built on Selenium + BeautifulSoup.
No hardcoded site configs — everything is detected at runtime.
"""

from itertools import product
from collections import Counter
import logging
import re
from time import sleep
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service

from itertools import chain

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

# -- Copilot kokade ? Är menat att hjälpa sortera bilder -------------------------------------------------------


# -----------------------------
# Helper: Convert a character to a regex class (paper Stage 1)
# -----------------------------

def char_to_regex(c):
    if c.isdigit():
        return r"\d"
    if c.isalpha():
        if c.islower():
            return r"[a-z]"
        if c.isupper():
            return r"[A-Z]"
    if c in ["/", ":", ".", "-", "_", "="]:
        return re.escape(c)
    return "."  # wildcard for anything else


# -----------------------------
# Helper: Convert full string into generalized regex tokens
# Similar—but simplified—to Stage 1 of the paperfrom selenium.webdriver.chrome.service import Service
# -----------------------------
def generalize_string(s):
    return "".join(char_to_regex(c) for c in s)


# -----------------------------
# Core Algorithm
# -----------------------------
def infer_regex_classifier(positives, negatives, max_candidates=200, min_precision=0.75):
    """
    Given:
        positives = list of relevant image URLs
        negatives = list of irrelevant image URLs

    Returns:
        best_regex  (string)
    """

    # 1) Generate base generalized regexes for each positive sample
    base_patterns = [generalize_string(p) for p in positives]

    # 2) Combine them into candidate regexes by creating OR groups
    #    (approximate Stage 2 alignment without Levenshtein)
    candidates = set()

    # simple 1-pattern candidates
    candidates.update(base_patterns)

    # 2-pattern OR combinations
    for a, b in product(base_patterns, base_patterns):
        if a != b:
            candidates.add(f"(?:{a})|(?:{b})")

    # Limit candidate explosion
    candidates = list(candidates)[:max_candidates]

    # 3) Evaluate candidates (Stage 3)
    best_regex = None
    best_f1 = -1

    for pattern in candidates:
        try:
            regex = re.compile(pattern)
        except re.error:
            continue

        pos_matches = sum(1 for p in positives if regex.search(p))
        neg_matches = sum(1 for n in negatives if regex.search(n))

        if pos_matches == 0:
            continue

        precision = pos_matches / (pos_matches + neg_matches + 1e-9)
        recall = pos_matches / len(positives)
        f1 = 2 * (precision * recall) / (precision + recall + 1e-9)

        if precision >= min_precision and f1 > best_f1:
            best_f1 = f1
            best_regex = pattern

    return best_regex


# -----------------------------
# Applying it to BeautifulSoup
# -----------------------------
def filter_relevant_images(soup, positives, negatives):
    """
    soup       = a BeautifulSoup page
    positives  = sample relevant image URLs
    negatives  = sample irrelevant image URLs
    """

    best_regex = infer_regex_classifier(positives, negatives)
    if not best_regex:
        return []  # fallback

    pattern = re.compile(best_regex)

    return [
        img["src"]
        for img in soup.find_all("img", src=True)
        if pattern.search(img["src"])
    ]
# -- Copilot kokade ? Är menat att hjälpa sortera bilder -------------------------------------------------------


# ── URL helpers ────────────────────────────────────────────────────────────────

def is_valid_url(url: str) -> bool:
    try:
        p = urlparse(url)
        return p.scheme in ("http", "https") and bool(p.netloc)
    except Exception:
        return False


# Unnecessary?
def is_navigable_href(href: str) -> bool:
    if not href:
        return False
    s = href.strip().lower()
    return not any(s.startswith(p) for p in
                   ("#", "/", "javascript:", "mailto:", "tel:", "data:", "blob:"))

# Unnecessary?


def get_domain(url: str) -> str:
    p = urlparse(url)
    return f"{p.scheme}://{p.netloc}"


def get_website_name(url: str) -> str:
    netloc = urlparse(url).netloc.lower().replace("www.", "")
    return netloc.split(".")[0]


def resolve_url(href: str, base_url: str) -> str | None:
    """Turn a relative href into an absolute URL."""
    if not href:
        return None
    full = urljoin(base_url, href.strip())
    return full if is_valid_url(full) else None


# ── Browser setup ──────────────────────────────────────────────────────────────


def build_driver(headless: bool = True) -> webdriver.Chrome:
    options = Options()
    if headless:
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--incognito")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    service = Service("/usr/bin/chromedriver")
    return webdriver.Chrome(service=service, options=options)


# ── Generic popup removal ──────────────────────────────────────────────────────

# Common selectors for cookie banners and modals — no hardcoded domains needed
_POPUP_SELECTORS = [
    # Buttons by text (case-insensitive substring match via XPath)
    "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'accept')]",
    "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'agree')]",
    "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'close')]",
    "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'dismiss')]",
    "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'got it')]",
    "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'no thanks')]",
    "//*[@id='onetrust-accept-btn-handler']",
    "//*[@id='cookie-accept']",
    "//*[contains(@class,'cookie-close')]",
    "//*[contains(@class,'modal-close')]",
    "//*[contains(@class,'popup-close')]",
    "//*[contains(@aria-label,'close')]",
]

_HARDCODED_XPATHS = [
    # Amazon's bot detection overlay
    '/html/body/div/div[1]/div[3]/div/div/form/div/div/span',
    # Facebook's cookie consent dialog
    '/html/body/div[2]/div[1]/div/div[2]/div/div/div/div/div[2]/div/div[1]/div[2]',
    '/html/body/div[1]/div/div[1]/div/div[5]/div/div/div[1]/div/div[2]/div/div/div/div[1]/div',
    # Elgiganten's cookie banner
    '/html/body/div[1]/div[1]/div/div[1]/div[3]/div/button[3]',
]

# BOTTLE NECK FOR SPEEEEED, OPTIMIZE by knowing when to use?


def remove_popups(driver: webdriver.Chrome) -> None:
    """Try to dismiss any generic overlay/popup/cookie banner."""
    sleep(2)  # Wait for website to load
    for xpath in chain(_HARDCODED_XPATHS, _POPUP_SELECTORS):
        try:
            btn = WebDriverWait(driver, 0.5).until(
                EC.element_to_be_clickable((By.XPATH, xpath)))
            btn.click()
            log.info("Dismissed popup via: %s", xpath)
        except Exception:
            pass  # Selector not present — move on


# ── Page loading ───────────────────────────────────────────────────────────────

def wait_for_page(driver: webdriver.Chrome, timeout: int) -> bool:
    """Wait until document.readyState == 'complete'. Returns False on timeout."""
    try:
        WebDriverWait(driver, timeout).until(lambda d: d.execute_script(
            "return document.readyState") == "complete")
        return True
    except TimeoutException:
        log.warning("Page load timed out after %ds.", timeout)
        return False


def scroll_page(driver: webdriver.Chrome, pause: float = 1.0) -> None:
    """Scroll to the bottom incrementally to trigger lazy-loaded content."""
    last_height = 0
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        sleep(pause)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


# ── Generic extractors ─────────────────────────────────────────────────────────

def extract_images(soup: BeautifulSoup, base_url: str) -> list[str]:
    """
    Collect image URLs from:
      - <img src> and <img data-src> (lazy loading)
      - <source srcset> inside <picture>
      - any src-like attribute containing an image extension
    """
    images = set()
    # Match common image extensions in URLs (e.g. ?fmt=jpg)
    img_ext = re.compile(
        # extension anywhere before params
        r'\.(jpg|jpeg|png|webp|gif|svg|pjpeg)(\?[^&]*)?(&.*)?$'
        # fmt= query param
        r'|[?&]fmt=(jpg|jpeg|png|webp|gif|svg|pjpeg)'
        # Scene7 / AEM image URLs
        r'|/is/image/',
        re.I
    )

    for tag in soup.find_all('img'):
        for attr in ('src', 'data-src', 'data-lazy-src', 'data-original'):
            src = tag.get(attr)
            if src:
                full = resolve_url(src, base_url)
                if full:
                    images.add(full)

        # Handle srcset separately — it's a comma-separated list of "url width" pairs
        srcset = tag.get('srcset', '')
        for part in srcset.split(','):
            parts = part.strip().split()
            if parts:
                full = resolve_url(parts[0], base_url)
                if full:
                    images.add(full)

    return [u for u in images if img_ext.search(u)]


'''def extract_links(soup: BeautifulSoup, base_url: str) -> list[str]:
    """Return all unique navigable absolute links on the page."""
    links = set()
    for tag in soup.find_all('a', href=True):
        href = tag['href']
        if is_navigable_href(href):
            full = resolve_url(href, base_url)
            if full:
                links.add(full)
    return list(links)'''


'''def extract_text(soup: BeautifulSoup) -> dict:
    """
    Extract structured text without relying on site-specific selectors.
    Heuristically identifies title, headings, paragraphs, and price-like strings.
    """
    # Remove clutter tags
    for tag in soup(['script', 'style', 'nav', 'footer', 'header',
                     'aside', 'form', 'noscript']):
        tag.decompose()

    title = soup.title.string.strip() if soup.title and soup.title.string else ""

    headings = []
    for level in ('h1', 'h2', 'h3'):
        for tag in soup.find_all(level):
            text = tag.get_text(strip=True)
            if text:
                headings.append({"level": level, "text": text})

    paragraphs = [
        p.get_text(strip=True)
        for p in soup.find_all('p')
        if len(p.get_text(strip=True)) > 40   # skip tiny/empty paragraphs
    ]

    # Generic price detection — finds patterns like $9.99, €12, £5.50
    price_pattern = re.compile(r'[\$€£¥₹]\s?\d+[\.,]?\d*')
    prices = list(set(price_pattern.findall(soup.get_text())))

    return {
        "title": title,
        "headings": headings,
        "paragraphs": paragraphs,
        "prices": prices,
    }'''


'''def extract_metadata(soup: BeautifulSoup) -> dict:
    """Pull Open Graph, Twitter Card, and standard meta tags."""
    meta = {}
    for tag in soup.find_all('meta'):
        name  = tag.get('property') or tag.get('name') or tag.get('itemprop')
        value = tag.get('content')
        if name and value:
            meta[name] = value.strip()
    return meta'''


# ── Main scraping entry point ──────────────────────────────────────────────────

def scrape(url: str, timeout: int = 15, scroll: bool = False, headless: bool = True) -> dict | None:
    """
    Scrape a single URL and return a dict with:
      - url, website_name
      - images (list of absolute URLs)
      - links  (list of absolute URLs)
      - text   (title, headings, paragraphs, prices)
      - meta   (Open Graph / meta tags)
    Returns None on failure.
    """
    if not is_valid_url(url):
        log.error("Invalid URL: %s", url)
        return None

    website_name = get_website_name(url)
    driver = build_driver(headless=headless)

    try:
        log.info("Loading %s ...", url)
        driver.get(url)

        remove_popups(driver)

        loaded = wait_for_page(driver, timeout)
        if not loaded:
            # Still try — partial content is better than nothing
            log.warning("Proceeding with partially loaded page.")
            # return None ?

        if scroll:
            scroll_page(driver)

        html = driver.page_source

    except WebDriverException as exc:
        log.exception("WebDriver error: %s", exc)
        return None
    finally:
        driver.quit()

    soup = BeautifulSoup(html, 'html.parser')

    return {
        "url":          url,
        "website_name": website_name,
        "images":       extract_images(soup, url),
        # "links":        extract_links(soup, url),
        # "text":         extract_text(soup),
        # "meta":         extract_metadata(soup),
    }


def get_scraping_data(url: str) -> dict | None:
    """
    Public interface — scrapes the URL and retries once with a
    longer timeout if the first attempt returns nothing.
    """
    result = scrape(url, timeout=15)
    if result is None:
        log.info("Retrying with extended timeout...")   # Funkar ej
        result = scrape(url, timeout=30)
    return result


# ── Quick demo ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import json

    test_urls = [
        "https://www.amazon.com/Bordered-Silicone-Dressing-Waterproof-Breathable/dp/B08BWGVGTP/ref=sr_1_1_sspa?dib=eyJ2IjoiMSJ9.ZV02BNtZXQoBrqQQIy9y-SnmgOmsmvyGQLIc9ZByv9arLpVWq_HFnmLqMaR1Byh-HJRqWCg867DH7PjNGbSR0hmZ2lBLLgGPqGj-QoyF_xTjJmyYb7gcGQ-BebuYS-fgCsreiKdeohhTr6I2SFC0jfgZ1p1rO9ChKjt3QeuIjKIaSBS_NGZ-4hH2S4yOrZwYVpHFrM9mDOQV6bQM6AcjhHQNdpCYA8XhywCPwQhAUZQ.2PRPBRdM7jFg47JBiUcDXpWP7ZSAhGrNSccrwWuXH_s&dib_tag=se&keywords=m%C3%B6lnlycke&qid=1772530320&sr=8-1-spons&sp_csd=d2lkZ2V0TmFtZT1zcF9hdGY&th=1",
        "https://www.temu.com/gaming-headset-p-34567891234.html",
        "https://www.ebay.com/itm/389340071774?epid=12064992096&itmmeta=01KM0K23NBX0V20S7D8CDZBPXQ&hash=item5aa67a075e:g:VQ0AAeSwpKVpNFSE&itmprp=enc%3AAQALAAAA4DKQclQvzFwZQpmMrsO4Luqz69MrBeOo8uj8ZHREq4xNOi0pbtrRJ2Tg7lwpdPOKVgN7KkLGYZktWCh4JK1xPBR6hDDTI26MLFKcatNvP0OMh8HKz8bMsp%2FyMwxSPMLo2e59PMdpdtHvLhfio7HsM%2BvTzLV7MVbObda4Fzcv%2FPdPPZhDyZ%2FmPNv%2Fvdefjm%2Fk5PPOi%2FLTxLRtmOZgVmIHSk%2Bi7SvvCbE8HE%2FbIz4cyLeLJ%2BCR13rQNlhEgNXhW%2B2kKlON%2FjHpMpluNRoV0%2BrVnYqPcq8--Mq%2BxGdqswKRCgrU%7Ctkp%3ABFBM7rqIk6Bn&var=656654952199",
        "https://www.aliexpress.com/item/1005011643932033.html?spm=a2g0o.productlist.main.2.358a5938uzfmeH&algo_pvid=1b7fa8ef-4bd4-42d1-87cd-22c499bfbf5f&algo_exp_id=1b7fa8ef-4bd4-42d1-87cd-22c499bfbf5f-1&guide_trace=353c8c2a-d6bb-4cd7-b142-d5646b6a2f4e&pdp_ext_f=%7B%22order%22%3A%223%22%2C%22spu_best_type%22%3A%22price%22%2C%22eval%22%3A%221%22%2C%22fromPage%22%3A%22search%22%7D&pdp_npi=6%40dis%21SEK%21784.39%21377.91%21%21%21567.25%21273.29%21%402103894417738415382443836eaf8e%2112000056134741775%21sea%21SE%210%21ABX%211%210%21n_tag%3A-29910%3Bd%3A18dd2014%3Bm03_new_user%3A-29895%3BpisId%3A5000000197850273&curPageLogUid=8HHjkrxVlcX0&utparam-url=scene%3Asearch%7Cquery_from%3Acategory_navigate%7Cx_object_id%3A1005011643932033%7C_p_origin_prod%3A",
        "https://www.etsy.com/se-en/listing/1765280597/vintage-fall-sunset-print-autumn?ls=r&ref=rlp-listing-grid-2&external=1&space_id=1314272294773&pro=1&sts=1&dd=1&content_source=3845fe3a9163771f60e9588887d8deee%253ALT17be2aaccb6c48ed7cb372699703c3d3581b62f5&logging_key=3845fe3a9163771f60e9588887d8deee%3ALT17be2aaccb6c48ed7cb372699703c3d3581b62f5",
        "https://www.walmart.com/ip/KONG-Dr-Noys-Plush-Frog-Squeaker-Dog-Toy/19629165?athAsset=eyJhdGhjcGlkIjoiMTk2MjkxNjUiLCJhdGhzdGlkIjoiQ1MwMjAiLCJhdGhhbmNpZCI6Ikl0ZW1DYXJvdXNlbCIsImF0aHJrIjowLjB9&athena=true",
        "https://www.facebook.com/marketplace/item/5511004022338405/",
        "https://www.target.com/p/what-do-you-meme-emotional-support-minis-chocolate-bunnies-stuffed-animal/-/A-94961278#lnk=sametab",
        "https://www.blocket.se/mobility/item/21419403",
        "https://www.elgiganten.se/product/vitvaror/tvatt-tork/tvattmaskin/electrolux-serie-600-tvattmaskin-efi622ex4e105kg/966285",
    ]

    for url in test_urls:
        data = get_scraping_data(url)

        if data:
            # Print a readable summary
            print(f"\n{'='*60}")
            print(f"  {data['website_name'].upper()}  —  {data['url']}")
            print(f"{'='*60}")
            # print(f"Title     : {data['text']['title']}")
            print(f"Images    : {len(data['images'])}")
            # print(f"Links     : {len(data['links'])}")
            # print(f"Paragraphs: {len(data['text']['paragraphs'])}")
            # print(f"Prices    : {data['text']['prices']}")
            # print(f"Meta tags : {len(data['meta'])}")
            # print(f"\nFull result (JSON):")
            print(json.dumps(data, indent=2, default=str))
        else:
            print("Scraping failed.")
