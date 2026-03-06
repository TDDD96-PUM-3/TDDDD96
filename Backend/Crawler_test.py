from bs4 import BeautifulSoup
#import requests
import re

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from time import sleep

from urllib.parse import urlparse, parse_qs, urlencode, urlunparse, unquote

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

def print_data(link, name, links_to_explore):
    # Save the link to explore later
    if name == "amazon":
        clean_link = clean_amazon_url(link)
    elif name == "facebook":
        clean_link = clean_facebook_url(link)
    links_to_explore.add(clean_link)

    #Show the title and link for the main products on the page
    print(f'Link: {clean_link}')
    print('---')


def get_links_data(soup, name, links_to_explore):
    for a in soup.find_all('a', href=True):
        link = a['href']
        # Save the link to explore later
        print_data(link, name, links_to_explore)
    
    

def search_new_link(driver,url):
    try:
        driver.get(url)  # Load the product page
        sleep(1)  # Wait for the page to load before exploring the next link
        html = driver.page_source        # Pass the HTML to BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')

        return soup
    except WebDriverException as e:
        logging.exception("WebDriver error:", e)


def get_data(url, name, base  = None):
    links_to_explore = set()
    deapth = 0

    options = Options()
    options.add_argument("--incognito")
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(options=options)  # Ensure ChromeDriver is installed and in PATH

    try:
        if base:
            driver.get(base)
            sleep(3)  # Wait for the page to load
        soup = search_new_link(driver, url)  # Load the page
    except WebDriverException as e:
        logging.exception("WebDriver error:", e)

    # Explore the search results and get the links to the product pages
    get_links_data(soup, name, links_to_explore)

    while len(links_to_explore) > 0 and deapth < 1:
        link = links_to_explore.pop()  # Get the first link from the list
        soup = search_new_link(driver,link)  # Load the product page  # Wait for the page to load before exploring the next link
        if soup != None:
            get_links_data(soup, name, links_to_explore)
        deapth += 1

    driver.quit()  # Close the browser when done

    return links_to_explore

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
    from urllib.parse import urlparse
    hostname = urlparse(url).netloc.lower()

    for name, config in MARKETPLACE_PATTERNS.items():
        if config["domain_keyword"] in hostname:
            return name

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

    name = get_marketplace(url) or "unknown"

    test_urls = get_data(url, name, base)
    number_of_products = 0
    
    for url in test_urls:
        result = "✅" if is_product_url(url) else "❌"
        if result == "✅":
            number_of_products += 1
            print(f"{result} [{name:12}] {url}")

    print(f"Total number of products found: {number_of_products}")
