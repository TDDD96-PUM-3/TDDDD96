from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import WebDriverException

import logging

from urllib.parse import urlparse

from time import sleep

import re

# ── Input validation ───────────────────────────────────────────────────────────
# Should be moved so crawler and scraper can share the same validation functions
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

def scroll_page(driver):
    last_height = 0
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        sleep(1)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break  # reached the bottom
        last_height = new_height

POPUP_SITES_PRESSHOLD = {
        "walmart": {
        "domain_keyword": "walmart",
        "Xpath": [
            '/html/body/div/div',
        ],
    },
}


POPUP_SITES = {
    "amazon": {
        "domain_keyword": "amazon",
        "Xpath": [
            '/html/body/div/div[1]/div[3]/div/div/form/div/div/span',
        ],
    },

    "etsy": {
        "domain_keyword": "etsy",
        "Xpath": [
            r'https://i\.etsystatic\.com/.*\.(jpg|jpeg|png|webp)',
        ],
    },

    "facebook": {
        "domain_keyword": "facebook",
        "Xpath": [
            '/html/body/div[2]/div[1]/div/div[2]/div/div/div/div/div[2]/div/div[1]/div[2]',
            '/html/body/div[1]/div/div[1]/div/div[5]/div/div/div[1]/div/div[2]/div/div/div/div[1]/div',
        ],
    },
}

IMAGE_CDN_PATTERNS = {
    "amazon": {
        "domain_keyword": "amazon",
        "image_patterns": [
            r'https://m\.media-amazon\.com/images/.*\.(jpg|jpeg|png|webp)',
            r'https://images-na\.ssl-images-amazon\.com/images/.*\.(jpg|jpeg|png|webp)',
            r'https://images-eu\.ssl-images-amazon\.com/images/.*\.(jpg|jpeg|png|webp)',
        ],
    },

    "temu": {
        "domain_keyword": "temu",
        "image_patterns": [
            r'https://img\.ltwebstatic\.com/.*\.(jpg|jpeg|png|webp)',
            r'https://aimg\.kwcdn\.com/.*\.(jpg|jpeg|png|webp)',
        ],
    },

    "ebay": {
        "domain_keyword": "ebay",
        "image_patterns": [
            r'https://i\.ebayimg\.com/images/.*\.(jpg|jpeg|png|webp)',
            r'https://ir\.ebaystatic\.com/.*\.(jpg|jpeg|png|webp)',
        ],
    },

    "aliexpress": {
        "domain_keyword": "aliexpress",
        "image_patterns": [
            r'https://ae01\.alicdn\.com/kf/.*\.(jpg|jpeg|png|webp)',
            r'https://.*\.alicdn\.com/.*\.(jpg|jpeg|png|webp)',
        ],
    },

    "etsy": {
        "domain_keyword": "etsy",
        "image_patterns": [
            r'https://i\.etsystatic\.com/.*\.(jpg|jpeg|png|webp)',
        ],
    },

    "walmart": {
        "domain_keyword": "walmart",
        "image_patterns": [
            r'https://i5\.walmartimages\.com/.*\.(jpg|jpeg|png|webp)',
            r'https://i\d\.walmartimages\.com/.*\.(jpg|jpeg|png|webp)',
        ],
    },

    "facebook": {
        "domain_keyword": "facebook",
        "image_patterns": [
            r'https://scontent.*\.fbcdn\.net/.*\.(jpg|jpeg|png|webp)',
        ],
    },

    "target": {
        "domain_keyword": "target",
        "image_patterns": [
            r'https://target\.scene7\.com/is/image/.*',
            r'https://.*\.target\.com/.*\.(jpg|jpeg|png|webp)',
        ],
    },

    "craigslist": {
        "domain_keyword": "craigslist",
        "image_patterns": [
            r'https://images\.craigslist\.org/.*\.(jpg|jpeg|png|webp)',
        ],
    },
}

# ── Scraping functions ────────────────────────────────────────────────────────
'''def get_images(soup, website_name):
    if website_name not in IMAGE_CDN_PATTERNS:
        return None

    images = set()    
    patterns = IMAGE_CDN_PATTERNS[website_name]["image_patterns"]
    for pattern in patterns:
        found = soup.find_all('img', src=re.compile(pattern, re.I))
        images.update(img.get('src') for img in found if is_valid_url(img.get('src')) and is_navigable_href(img.get('src')))


    return images'''

def get_images(soup, website_name):
    images = set()

    # If we don't have specific patterns for the website, just return all img tags (with src that is a valid URL)
    if website_name not in IMAGE_CDN_PATTERNS:
        found = soup.find_all('img')
        images.update(img for img in found)

    else:   
        patterns = IMAGE_CDN_PATTERNS[website_name]["image_patterns"]
        for pattern in patterns:
            found = soup.find_all('img', src=re.compile(pattern, re.I))
            images.update(img.get('src') for img in found if is_valid_url(img.get('src')) and is_navigable_href(img.get('src')))

    return images

def remove_popups(driver, website_name):
    if website_name in POPUP_SITES:
        # Websites with known pop-ups that can be removed by clicking specific XPaths
        xpaths = POPUP_SITES[website_name]["Xpath"]
        # Remove pop-ups by known XPaths for the website.
        for xpath in xpaths:
            try:
                btn = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, xpath)))
                btn.click()
                sleep(1)  # Allow website to load
                print("Popup removed")
            except Exception:
                pass
        return
    elif website_name in POPUP_SITES_PRESSHOLD:
        print("Trying to remove pop-up by press and hold...")
        for xpath in POPUP_SITES_PRESSHOLD[website_name]["Xpath"]:
            try:
                element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, xpath)))
                break  # found it, exit loop
            except Exception:
                continue

        else:
            return  # no pattern matched, exit function safely

        action = ActionChains(driver)
        action.click_and_hold(on_element=element)
        action.perform()   
        sleep(5)                                # perform the operation
        return
    else:
        print(website_name)
        return  # No known pop-ups for this website


def start_scraping(url, website_name, timeout=15):
    # Ta bort ?
    if url is None:
        print("No URL provided for scraping.")
        return None
    
    # run without opening a window
    options = Options()
    #options.add_argument("--headless")        
    #options.add_argument("--disable-gpu") 

    options.add_argument("--no-sandbox")        # required in Docker
    options.add_argument("--disable-dev-shm-usage")  # prevents memory issues in Docker

    # Enable incognito mode and disable automation flags to avoid user data contamination and detection by websites
    options.add_argument("--incognito")
    options.add_argument("--disable-blink-features=AutomationControlled")

    # Disable Selenium automation flags to make the browser less detectable as a bot
    '''options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)'''

    driver = webdriver.Chrome(options=options)  # Ensure ChromeDriver is installed and in PATH


    # NOT NECISARILY NEEDED, BUT SOME WEBSITES MAY DETECT BOT IF NOT STARTING FROM HOMEPAGE
    # Start the homepage before going to product page to avoid bot detection
    try:
        if website_name == "mmmmm": # For loop med hemsidor
            domain = get_domain(url)
            if not is_valid_url(domain):
                logging.warning("Invalid base URL provided: %s — skipping.", domain)
                return None
            print(f"Navigating to domain homepage: {domain}")
            driver.get(domain)
            sleep(3)  # Wait for the page to load       
    except WebDriverException as e:
        logging.exception("WebDriver error during scraping:", e)
        driver.quit()
        return None
    # //////////////////////////////////////////////////////////////////////////
    

    driver.get(url)  # Load the page
    remove_popups(driver, website_name)  # Remove pop-ups after loading the page

    # Load the page and wait until the main content is present
    try:
        print("Waiting for page to load...")
        WebDriverWait(driver, timeout).until(lambda d: d.execute_script("return document.readyState") == "complete")
    except TimeoutException:
        print("Page took too long to load")
        driver.quit()
        return None
    else:
        # Scroll to the bottom of the page to load all images (for lazy loading)
        # scroll_page(driver)

        # Get the page source (HTML) after rendering
        html = driver.page_source

        # Pass the HTML to BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')

        images = get_images(soup, website_name)

    driver.quit()
    return {"images": images}

# ── Lookup helpers ─────────────────────────────────────────────────────────────

def get_website_name(url: str) -> str | None:
    #Return website_name name by checking if its keyword appears in the hostname.
    hostname = urlparse(url).netloc.lower()

    # Match name in URL to known websites
    for website_name, config in IMAGE_CDN_PATTERNS.items():
        if config["domain_keyword"] in hostname:
            return website_name
    else:
        # Extract the website name from a generic URL
        parsed = urlparse(url)
        domain = parsed.netloc.replace("www.", "")  # remove www.
        name = domain.split('.')[0]                  # take first part before the dot
        return name


def get_domain(url: str) -> str:
    """Extract the domain from a given URL, e.g. 'amazon.com'"""
    parsed = urlparse(url)
    # Remove 'www.' if present
    domain = parsed.netloc.replace("www.", "")
    domain = "https://" + domain
    return domain


# Keeps track of timeout for the scraping process, if it takes too long, it will stop and return None
def get_scraping_data(url):
    if url is None:
        return None
    
    website_name = get_website_name(url)  # Determine website_name from URL
    result = start_scraping(url, website_name)  # Start scraping with default timeout

    # See if website is not responding, if so, retry once
    if result is None:
        print("Retrying scraping with increased timeout...")
        return start_scraping(url, website_name, timeout=30)  # Retry with new timeout limit
    
    return result

    