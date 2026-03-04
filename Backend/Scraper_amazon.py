from bs4 import BeautifulSoup
import requests
import re

from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep

def get_item_details(soup):
    # Extract the data from the table containing the product details
    value = soup.find_all('td', class_='a-size-base voyager-ns-desktop-table-value')
    category = soup.find_all('th', class_='a-color-secondary a-size-base voyager-ns-desktop-table-label')

    print(f'Found {len(category)} categories and {len(value)} values:')
    # Return a list of tuples containing the category and its corresponding information
    return [(cat.get_text(strip=True), val.get_text(strip=True)) for cat, val in zip(category, value)]


def get_top_highlights(soup):
    # Extract the data from the table containing the product details
    value = soup.find_all('td', class_='a-span9', role='presentation')
    category = soup.find_all('td', class_='a-span3', role='presentation')

    print(f'Found {len(category)} categories and {len(value)} values:')
    # Return a list of tuples containing the category and its corresponding information
    return [(cat.find("span").get_text(strip=True), val.find("span").get_text(strip=True)) for cat, val in zip(category, value)]


def get_seller_info(soup):
    # Extract the seller information
    seller_info = soup.find('a', class_='a-size-small a-link-normal offer-display-feature-text-message').get_text(strip=True)
    return seller_info



def get_review_data(soup):
    # Extract the data from the reviews section
    reviews = soup.find_all('li', attrs={"data-hook": "review"})
    reviews_text = [review.find('div', class_="a-expander-content reviewText review-text-content a-expander-partial-collapse-content") for review in reviews]
    reviews_stars = [review.find('i', class_=re.compile(r"a-icon a-icon-star a-star\b") ) for review in reviews]  # Match class that starts with "a-icon a-icon-star review-rating"

    print(f'Found {len(reviews_stars)} stars and {len(reviews_text)} reviews:')
    # Return a list of tuples containing the review text and its corresponding star rating
    return [(review.find("span").get_text(strip=True), star.find("span").get_text(strip=True)) for star, review in zip(reviews_stars, reviews_text)]


# TEST
if __name__ == "__main__":
    links_to_explore = []
    deapth = 0

    url = "https://www.amazon.com/"
    driver = webdriver.Chrome()  # Ensure ChromeDriver is installed and in PATH
    driver.get(url)
    sleep(1)  # Wait for the page to load
    #driver.get("https://www.amazon.com/s?k=mölnlycke")  # Load the page
    #sleep(3)  # Wait for the page to load
    driver.get("https://www.amazon.com/Bordered-Silicone-Dressing-Waterproof-Breathable/dp/B08BWGVGTP/ref=sr_1_1_sspa?th=1")  # Load the page

    # Get the page source (HTML) after rendering
    html = driver.page_source

    # Pass the HTML to BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    # Explore the search results and get the links to the product pages

    highlights = get_top_highlights(soup)
    print(highlights)
    details = get_item_details(soup)
    print(details)
    seller = get_seller_info(soup)
    print(seller)
    reviews = get_review_data(soup)
    print(reviews)

    driver.quit()
    
    