"""
universal_scraper.py
────────────────────
A site-agnostic scraper built on Selenium + BeautifulSoup.
No hardcoded site configs — everything is detected at runtime.
"""

import logging
import random
import time
import re
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import undetected_chromedriver as uc


# Kan tas bort om manuell när images = 0 implementeras
# Kan implementera en begränsning på mängden bilder eftersom det går uppifrån och ner
_POPUP_SELECTORS = [
    # ── Scoped to dialog/overlay containers ──────────────────────────────
    # Only match buttons INSIDE elements that look like popups
    "//*[@role='dialog' or @role='alertdialog' or contains(@class,'modal') or contains(@class,'popup') or contains(@class,'overlay') or contains(@class,'cookie') or contains(@class,'consent') or contains(@class,'gdpr') or contains(@id,'cookie') or contains(@id,'consent') or contains(@id,'gdpr')]//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'accept')]",
    "//*[@role='dialog' or @role='alertdialog' or contains(@class,'modal') or contains(@class,'popup') or contains(@class,'overlay') or contains(@class,'cookie') or contains(@class,'consent') or contains(@class,'gdpr') or contains(@id,'cookie') or contains(@id,'consent') or contains(@id,'gdpr')]//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'agree')]",
    "//*[@role='dialog' or @role='alertdialog' or contains(@class,'modal') or contains(@class,'popup') or contains(@class,'overlay') or contains(@class,'cookie') or contains(@class,'consent') or contains(@class,'gdpr') or contains(@id,'cookie') or contains(@id,'consent') or contains(@id,'gdpr')]//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'ok')]",
    "//*[@role='dialog' or @role='alertdialog' or contains(@class,'modal') or contains(@class,'popup') or contains(@class,'overlay') or contains(@class,'cookie') or contains(@class,'consent') or contains(@class,'gdpr') or contains(@id,'cookie') or contains(@id,'consent') or contains(@id,'gdpr')]//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'allow')]",
    "//*[@role='dialog' or @role='alertdialog' or contains(@class,'modal') or contains(@class,'popup') or contains(@class,'overlay') or contains(@class,'cookie') or contains(@class,'consent') or contains(@class,'gdpr') or contains(@id,'cookie') or contains(@id,'consent') or contains(@id,'gdpr')]//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'dismiss')]",
    "//*[@role='dialog' or @role='alertdialog' or contains(@class,'modal') or contains(@class,'popup') or contains(@class,'overlay') or contains(@class,'cookie') or contains(@class,'consent') or contains(@class,'gdpr') or contains(@id,'cookie') or contains(@id,'consent') or contains(@id,'gdpr')]//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'got it')]",

    # ── Specific IDs — safe, very unlikely to match non-popups ───────────
    "//*[@id='onetrust-accept-btn-handler']",
    "//*[@id='cookie-accept']",
    "//*[@id='accept-cookies']",
    "//*[@id='cookieConsent']",
    "//button[@data-wt-pbf='gdpr_accept_all']",

    # ── Specific classes — safe ───────────────────────────────────────────
    "//*[contains(@class,'cookie-close')]",
    "//*[contains(@class,'cookie-accept')]",
    "//*[contains(@class,'consent-accept')]",
    "//*[contains(@class,'gdpr-accept')]",

    # ── Aria labels scoped to buttons/roles only ──────────────────────────
    "//button[contains(translate(@aria-label,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'close cookie')]",
    "//button[contains(translate(@aria-label,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'accept cookie')]",

    # ── Span text → ancestor button (scoped to consent text only) ─────────
    "//span[contains(text(),'Accept all')]/ancestor::button",
    "//span[contains(text(),'Allow all cookies')]/ancestor::button",
    "//span[contains(text(),'Decline optional')]/ancestor::button",
    "//span[normalize-space(text())='OK']/ancestor::button",
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

# ── End of URL helpers ─────────────────────────────────────────────────────────

# ── Dependencies ───────────────────────────────────────────────────────────────
# ── Browser setup ──────────────────────────────────────────────────────────────


def build_driver(headless: bool = True) -> uc.Chrome:
    options = uc.ChromeOptions()

    options.add_argument("--lang=en-US")
    options.add_experimental_option('prefs', {
        'intl.accept_languages': 'en-US, en',
        # Dissable a narrow amount of pop-ups
        'profile.default_content_setting_values.notifications': 2, # 2 = block, 1 = allow
        'profile.default_content_setting_values.geolocation': 2,
        'profile.default_content_setting_values.media_stream': 2,
    })

    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")

    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--incognito")
    options.add_argument("--disable-blink-features=AutomationControlled")

    return uc.Chrome(options=options)

# ── Image extension regex ──────────────────────────────────────────────────────


def image_extension_regex() -> re.Pattern:
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
    return img_ext

# ── End of dependencies ────────────────────────────────────────────────────────

# ── Generic popup removal ──────────────────────────────────────────────────────

def remove_popups(driver: webdriver.Chrome) -> None:
    """Try to dismiss any generic overlay/popup/cookie banner."""
    combined_xpath = " | ".join(_POPUP_SELECTORS)
    try:
        # Identify all potential popups based on XPath
        elements = WebDriverWait(driver, 2).until(EC.presence_of_all_elements_located((By.XPATH, combined_xpath)))
        for el in elements:
            try:
                # Remove the popup by clicking it via JavaScript
                if el.is_displayed() and el.is_enabled():
                    driver.execute_script("arguments[0].click();", el)
                    log.info("Dismissed popup via element: %s", el.get_attribute("outerHTML")[:80])
            except Exception:
                pass
    except Exception:
        pass

# Idé för att låta användaren klicka bort popups manuellt om de inte kan identifieras automatiskt:
# Funkar dock inte just nu
def has_popup(driver) -> bool:
    return driver.execute_script("""
        return Array.from(document.querySelectorAll('*')).some(el => {
            const style = getComputedStyle(el);
            const zIndex = parseInt(style.zIndex);
            return (
                (style.position === 'fixed' || style.position === 'sticky' || style.position === 'absolute') &&
                style.display !== 'none' &&
                style.visibility !== 'hidden' &&
                style.opacity !== '0' &&
                !isNaN(zIndex) &&
                zIndex > 100
            );
        });
    """)


# ── Page loading ───────────────────────────────────────────────────────────────

# Oklart hur stor förbättring om något det ger
def wait_for_page(driver: webdriver.Chrome, timeout: int) -> bool:
    """Wait for page load with human-like timing to avoid bot detection."""
    try:
        # Randomize polling interval to avoid regular pattern
        WebDriverWait(driver, timeout, poll_frequency=random.uniform(0.3, 0.8)).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

        # Also wait for network to settle (no active XHR/fetch)
        WebDriverWait(driver, 3, poll_frequency=random.uniform(0.3, 0.6)).until(
            lambda d: d.execute_script("""
                return window.performance
                    .getEntriesByType('resource')
                    .filter(r => !r.responseEnd)
                    .length === 0
            """)
        )

        # Human-like pause after load before interacting
        time.sleep(random.uniform(0.5, 1.5))
        return True

    except TimeoutException:
        log.warning("Page load timed out after %ds.", timeout)
        return False


# ── Generic extractors ─────────────────────────────────────────────────────────

def extract_images(soup: BeautifulSoup, base_url: str, img_ext: re.Pattern) -> list[str]:
    """
    Collect image URLs from:
      - <img src> and <img data-src> (lazy loading)
      - <source srcset> inside <picture>
      - any src-like attribute containing an image extension
    """
    images = set()
    srcset_images = set()
   

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
                    srcset_images.add(full)

    return list(srcset_images) + [u for u in images if img_ext.search(u)]


def scrape(url: str, driver: webdriver.Chrome, timeout: int = 15, img_ext: re.Pattern = None, headless: bool = True) -> dict | None:
    """
    Scrape a single URL and return a dict with:
      - url, website_name
      - images (list of absolute URLs)
    Returns None on failure.
    """
    try:
        log.info("Loading %s ...", url)
        driver.get(url)
        loaded = wait_for_page(driver, timeout)

        remove_popups(driver)
        time.sleep(2)
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
        "images":       extract_images(soup, url, img_ext)
    }


def get_scraping_data(url: str, driver: webdriver.Chrome, img_ext: re.Pattern = None) -> dict | None:
    """
    Public interface — scrapes the URL and retries once with a
    longer timeout if the first attempt returns nothing.
    """
    if not is_valid_url(url):
        log.error("Invalid URL: %s", url)
        return None
    result = scrape(url, driver, timeout=15, img_ext=img_ext)
    if result is None:
        log.info("Retrying with extended timeout...")
        result = scrape(url, driver, timeout=30, img_ext=img_ext)
    return result
