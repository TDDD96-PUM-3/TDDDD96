from bs4 import BeautifulSoup
#import requests
import re

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from time import sleep

from urllib.parse import urlparse, parse_qs, urlencode, urlunparse, unquote, urljoin

import logging
import re

MARKETPLACE_PATTERNS = {
    "amazon": {
        "domain_keyword": "amazon",
        "product_patterns": [
            r'/dp/[A-Z0-9]',
            r'/gp/product/[A-Z0-9]',
            r'/exec/obidos/ASIN/[A-Z0-9]',
        ],
        "excluded_patterns": [
            r'/s\?', r'/s/', r'/b\?',
            r'/gp/cart', 
            r'/gp/checkout',
            r'/gp/your-account',
            r'/gp/help',
            r'/stores/',
            r'/ideas/',
            r'/wishlist/',
            r'/aax-us-east-retail-direct.amazon.com/',
        ]
    },

    "temu": {
        "domain_keyword": "temu",
        "product_patterns": [
            r'/[a-zA-Z0-9-]+-p-\d+',
            r'goods_id=\d+',
        ],
        "excluded_patterns": [
            r'/search', r'/category',
            r'/cart', r'/checkout',
            r'/account', r'/coupon',
        ]
    },

    "ebay": {
        "domain_keyword": "ebay",
        "product_patterns": [
            r'/itm/[a-zA-Z0-9-]*/\d{10,}',
            r'/itm/\d{10,}',
            r'item=\d{10,}',
        ],
        "excluded_patterns": [
            r'/sch/', r'/b/',
            r'/str/', r'/usr/',
            r'/mye/', r'/help/',
        ]
    },

    "aliexpress": {
        "domain_keyword": "aliexpress",
        "product_patterns": [
            r'/item/\d+\.html',
            r'/i/\d+\.html',
            r'productId=\d+',
        ],
        "excluded_patterns": [
            r'/category/', r'/wholesale/',
            r'/glosearch/', r'/af/',
            r'/store/', r'/feedback/',
        ]
    },

    "etsy": {
        "domain_keyword": "etsy",
        "product_patterns": [
            r'/listing/\d+/[a-zA-Z0-9-]+',
        ],
        "excluded_patterns": [
            r'/search', r'/shop/',
            r'/cart', r'/checkout',
            r'/account', r'/help',
            r'/market/',
        ]
    },

    "walmart": {
        "domain_keyword": "walmart",
        "product_patterns": [
            r'/ip/[a-zA-Z0-9-]+/\d+',
            r'/ip/\d+',
        ],
        "excluded_patterns": [
            r'/search', r'/browse',
            r'/cart', r'/checkout',
            r'/account', r'/store',
            r'/cp/',
        ]
    },

    "facebook": {
        "domain_keyword": "facebook",
        "product_patterns": [
            r'/marketplace/item/\d+',
        ],
        "excluded_patterns": [
            r'/marketplace/search',
            r'/marketplace/category',
            r'/marketplace/you',
            r'/marketplace/inbox',
        ]
    },

    "target": {
        "domain_keyword": "target",
        "product_patterns": [
            r'/p/[a-zA-Z0-9-]+-/-/A-\d+',
            r'preselect=\d+',
        ],
        "excluded_patterns": [
            r'/c/', r'/s\?',
            r'/cart', r'/checkout',
            r'/account', r'/store',
        ]
    },

    "craigslist": {
        "domain_keyword": "craigslist",
        "product_patterns": [
            r'/[a-z]+/d/[a-zA-Z0-9-]+/\d+\.html',
        ],
        "excluded_patterns": [
            r'/search/', r'/about/',
            r'/contact/', r'/account',
        ]
    },
}

# ── Input validation ───────────────────────────────────────────────────────────

def is_valid_url(url: str) -> bool:
    """Return True only if url has a scheme (http/https) and a non-empty netloc."""
    try:
        parsed = urlparse(url)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except Exception:
        return False


def is_navigable_href(href: str) -> bool:
    """
    Return False for hrefs that are not real page URLs:
    empty strings, anchors (#), javascript: pseudo-links, mailto:, tel:, etc.
    """
    if not href:
        return False
    stripped = href.strip()
    if stripped in ("#", "/"):
        return False
    lowered = stripped.lower()
    for prefix in ("javascript:", "mailto:", "tel:", "data:", "blob:"):
        if lowered.startswith(prefix):
            return False
    return True


# ── Data Printing Helpers ───────────────────────────────────────────────────────


def clean_url(href: str, website_name: str, page_url: str) -> str:
    # Normalise href to an absolute URL.
    if website_name == "amazon":
        return clean_amazon_url(href)
    if website_name == "facebook":
        return clean_facebook_url(href)
    else: 
        # Generic fallback: resolve relative URLs against the current page URL
        return urljoin(page_url, href)


def print_data(href, website_name, links_to_explore, visited_links: set, current_url: str):
    # Clean the URL based on the website's domain
    clean_link = clean_url(href, website_name, current_url)

    # Skip if already queued or visited
    if clean_link in visited_links or clean_link in links_to_explore:
        return

    links_to_explore.add(clean_link)

    #Show the title and link for the main products on the page
    print(f'Link: {clean_link}')
    print('---')


def get_links_data(soup, website_name, links_to_explore, visited_links: set, current_url: str):
    for a in soup.find_all('a', href=True):
        href = a['href']
        # Save the link to explore later
        if not is_navigable_href(href):
            continue

        print_data(href, website_name, links_to_explore, visited_links, current_url)
    
    

def search_new_link(driver,url):
    try:
        driver.get(url)  # Load the product page
        sleep(1)  # Wait for the page to load before exploring the next link
        html = driver.page_source        # Pass the HTML to BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        return soup
    except WebDriverException as e:
        logging.exception("WebDriver error:", e)
        return None


def get_data(url, website_name, base  = None):
    # ── Input validation ──────────────────────────────────────────────────────
    if not is_valid_url(url):
        logging.error("Invalid URL provided: %s", url)
        return set()

    if website_name == "unknown":
        logging.error("Unknown marketplace for URL: %s — aborting crawl.", url)
        return set()

    # ─ Setup ───────────────────────────────────────────────────────────────
    links_to_explore = set()
    visited_links = set()
    deapth = 0

    options = Options()
    options.add_argument("--incognito")
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(options=options)  # Ensure ChromeDriver is installed and in PATH

    try:
        if base:
            if not is_valid_url(base):
                logging.warning("Invalid base URL provided: %s — skipping.", base)
            else:
                driver.get(base)
                sleep(3)  # Wait for the page to load
                
        soup = search_new_link(driver, url)  # Load the page
        if soup is None:
            logging.error("Failed to load initial URL: %s", url)
            return set()

        # Explore the search results and get the links to the product pages
        visited_links.add(url)
        get_links_data(soup, website_name, links_to_explore)

        # ── Crawl loop ────────────────────────────────────────────────────
        while len(links_to_explore) > 0 and deapth < 1:
            link = links_to_explore.pop()  # Get the first link from the list
            visited_links.add(link)  # Mark the link as visited 
            
            soup = search_new_link(driver,link)  # Load the product page  # Wait for the page to load before exploring the next link
            if soup != None:
                get_links_data(soup, website_name, links_to_explore, visited_links, link)
            deapth += 1

    finally:
        driver.quit()  # Close the browser when done

    return visited_links

# ── URL Cleaning Helpers ─────────────────────────────────────────────────────

# Kanske ska flyttas till annan fil
def clean_amazon_url(href: str) -> str:
    base = "https://www.amazon.com"

    # Step 1: Make it absolute
    if href.startswith("/"):
        href = base + href

    parsed = urlparse(href)

    # Step 2: Unwrap /sspa/click redirect — real URL is in the `url` param
    if parsed.path.startswith("/sspa/click"):
        params = parse_qs(parsed.query)
        if "url" in params:
            # The inner URL is itself URL-encoded
            inner = unquote(params["url"][0])
            href = base + inner
            parsed = urlparse(href)

    # Step 3: Strip tracking query params, keep only essential ones
    keep = {"th", "psc"}  # keep variant selectors if needed, or just pass empty set
    filtered = {k: v for k, v in parse_qs(parsed.query).items() if k in keep}
    
    clean = parsed._replace(query=urlencode(filtered, doseq=True))
    return urlunparse(clean)


def clean_facebook_url(href: str) -> str:
    base = "https://www.facebook.com/"

    # Step 1: Make it absolute
    if href.startswith("/"):
        href = base + href

    return href

# ── Lookup helpers ─────────────────────────────────────────────────────────────

def get_marketplace(url: str) -> str | None:
    """Return marketplace name by checking if its keyword appears in the hostname."""
    hostname = urlparse(url).netloc.lower()

    for website_name, config in MARKETPLACE_PATTERNS.items():
        if config["domain_keyword"] in hostname:
            return website_name

    return None


def is_product_url(url: str) -> bool:
    """Return True if the URL points to a product page on a known marketplace."""
    marketplace = get_marketplace(url)
    if not marketplace:
        return False

    config = MARKETPLACE_PATTERNS[marketplace]

    if any(re.search(p, url, re.IGNORECASE) for p in config["excluded_patterns"]):
        return False

    return any(re.search(p, url, re.IGNORECASE) for p in config["product_patterns"])


# ── Example usage ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    base = "https://www.amazon.com"
    url = "https://www.amazon.com/s?k=mölnlycke"
    #url = "https://www.facebook.com/marketplace/?locale=sv_SE"

    website_name = get_marketplace(url) or "unknown"

    # website_name must be sent because the url might not contain the domain (e.g. amazon.com) 
    # and the cleanup would thereby not know which function to use
    test_urls = get_data(url, website_name, base)
    number_of_products = 0
    
    for url in test_urls:
        result = "✅" if is_product_url(url) else "❌"
        if result == "✅":
            number_of_products += 1
            print(f"{result} [{website_name:12}] {url}")

    print(f"Total number of products found: {number_of_products}")
