"""
universal_scraper.py
────────────────────
A site-agnostic scraper built on Selenium + BeautifulSoup.
No hardcoded site configs — everything is detected at runtime.
"""

import logging
import re
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from itertools import chain

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

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)


# ── URL helpers ────────────────────────────────────────────────────────────────

def is_valid_url(url: str) -> bool:
    try:
        p = urlparse(url)
        return p.scheme in ("http", "https") and bool(p.netloc)
    except Exception:
        return False


def resolve_url(href: str, base_url: str) -> str | None:
    """Turn a relative href into an absolute URL."""
    if not href:
        return None
    full = urljoin(base_url, href.strip())
    return full if is_valid_url(full) else None


def get_website_name(url: str) -> str:
    netloc = urlparse(url).netloc.lower().replace("www.", "")
    return netloc.split(".")[0]


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

    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


# ── Generic popup removal ──────────────────────────────────────────────────────

def remove_popups(driver: webdriver.Chrome) -> None:
    """Try to dismiss any generic overlay/popup/cookie banner."""
    wait_for_page(driver, timeout=2)
    for xpath in chain(_POPUP_SELECTORS):
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


def scrape(url: str, driver: webdriver.Chrome, timeout: int = 15, headless: bool = True) -> dict | None:
    """
    Scrape a single URL and return a dict with:
      - url, website_name
      - images (list of absolute URLs)
    Returns None on failure.
    """
    try:
        log.info("Loading %s ...", url)
        driver.get(url)

        remove_popups(driver)

        loaded = wait_for_page(driver, timeout)
        if not loaded:
            # Still try — partial content is better than nothing
            log.warning("Proceeding with partially loaded page.")
            # return None ?
        website_name = get_website_name(url)
        html = driver.page_source

    except WebDriverException as exc:
        log.exception("WebDriver error: %s", exc)
        return None

    soup = BeautifulSoup(html, 'html.parser')

    return {
        "url":          url,
        'name':         website_name,
        "images":       extract_images(soup, url)
    }


def get_scraping_data(url: str, driver: webdriver.Chrome) -> dict | None:
    """
    Public interface — scrapes the URL and retries once with a
    longer timeout if the first attempt returns nothing.
    """
    if not is_valid_url(url):
        log.error("Invalid URL: %s", url)
        return None
    result = scrape(url, driver, timeout=15)
    if result is None:
        log.info("Retrying with extended timeout...")
        result = scrape(url, driver, timeout=30)
    return result
