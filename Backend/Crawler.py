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

def print_data(link, title, links_to_explore):
    # Save the link to explore later
    clean_link = clean_amazon_url(link)
    links_to_explore.add(clean_link)

    #Show the title and link for the main products on the page
    print(f'Title: {title}')
    print(f'Link: {clean_link}')
    print('---')


def get_related_products_data(soup,links_to_explore):
    # Identifierar de varor som finns som rekommenderade på sidan, inte alla element som finns på sidan
    data = soup.find_all('div', class_="a-section sp_offerVertical p13n-asin sp_ltr_offer")  # Find all 'div' tags with role='listitem'
    print(f'Found {len(data)} items:')

    # Inspekt every div that data contains, to find the correct class for the title and link
    for item in data:
        title = item.find('div', class_=re.compile(r'sponsored-products')).text.strip()
        link = item.find('a', class_='a-link-normal')['href']
        # Save the link to explore later
        print_data(link, title, links_to_explore)

def get_search_result_data(soup,links_to_explore):
    data = soup.find_all('div', role='listitem')  # Find all 'div' tags with role='listitem'
    print(f'Found {len(data)} items:')

    for item in data:
        title = item.find('h2', class_=re.compile(r'a-size-medium a-spacing-none a-color-base a-text-normal')).text.strip()
        link = item.find('a')['href']
        print_data(link, title, links_to_explore)


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


def get_data():
    links_to_explore = set()
    deapth = 0

    options = Options()
    options.add_argument("--incognito")
    options.add_argument("--disable-blink-features=AutomationControlled")

    url = "https://www.amazon.com/"
    try:
        driver = webdriver.Chrome(options=options)  # Ensure ChromeDriver is installed and in PATH
        driver.get(url)
        sleep(3)  # Wait for the page to load
        driver.get("https://www.amazon.com/s?k=mölnlycke")  # Load the page
    except WebDriverException as e:
        logging.exception("WebDriver error:", e)

    # Get the page source (HTML) after rendering
    html = driver.page_source

    # Pass the HTML to BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    # Explore the search results and get the links to the product pages
    get_search_result_data(soup, links_to_explore)

    # Explore the product pages and get the links to the related products
    while len(links_to_explore) > 0 and deapth < 1:
        link = links_to_explore.pop()  # Get the first link from the list
        print(f'Exploring link: {link}')
        driver.get(link)  # Load the product page
        sleep(3)  # Wait for the page to load
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        get_related_products_data(soup, links_to_explore)
        deapth += 1

    driver.quit()  # Close the browser when done


if __name__ == "__main__":
    get_data()
    