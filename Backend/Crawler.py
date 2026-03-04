from bs4 import BeautifulSoup
import requests
import re

from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep

from urllib.parse import urlparse, parse_qs, urlencode, urlunparse, unquote

def get_data_selenium():
    '''
    #url = "https://www.svt.se/nyheter/lokalt/stockholm/"
    url = "https://www.amazon.se/s?k=mölnlycke"
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    print(page.status_code)  # Check if the request was successful
    #print(soup.prettify())  # Print the entire HTML content for debugging
    '''


    url = "https://www.amazon.com"
    driver = webdriver.Chrome()  # Make sure you have the ChromeDriver installed and in your PATH
    driver.get(url)
    sleep(3)  # Wait for the page to load
    driver.get("https://www.amazon.com/s?k=mölnlycke")  # Load the page

    data = driver.find_elements(By.CSS_SELECTOR, 'div[role="listitem"]')  # Find all 'article' elements with role='article'
    print(f'Found {len(data)} items:')

    for item in data:
        #Identifierar de varor som finns som fokus på sidan, inte alla element som finns på sidan
        title_element = item.find_element(By.CSS_SELECTOR, 'h2[class*="a-size-medium a-spacing-none a-color-base a-text-normal"] span')  # Find the 'span' element inside the 'h2' tag with specific class
        title = title_element.text.strip()
        link_element = item.find_element(By.TAG_NAME, 'a')
        link = link_element.get_attribute('href')

        #title_element = item.find_element(By.CSS_SELECTOR, 'a')  # Find the 'span' element inside the 'h2' tag with specific class
        #link = title_element.get_attribute('href' if re.match(r'^https://www.amazon.com', title_element.get_attribute('href')) else 'data-href')  # Get the 'href' attribute of the 'a' tag, checking if it starts with http or https    
        
        
        print(f'Title: {title}')
        print(f'Link: {link}')
        print('---')

    driver.quit()

#////////////////////////////////////////////////////////////////////////////////////////////////
#///////////////////////////////////////////////////////////////////////////////////////////////
#//////////////////////////////////////////////////////////////////////////////////////////////

def print_data(link, title, links_to_explore):
     # Save the link to explore later
    clean_link = clean_amazon_url(link)
    links_to_explore.append(clean_link)

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
    links_to_explore = []
    deapth = 0

    url = "https://www.amazon.com/"
    driver = webdriver.Chrome()  # Ensure ChromeDriver is installed and in PATH
    driver.get(url)
    sleep(3)  # Wait for the page to load
    driver.get("https://www.amazon.com/s?k=mölnlycke")  # Load the page

    # Get the page source (HTML) after rendering
    html = driver.page_source

    # Pass the HTML to BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    # Explore the search results and get the links to the product pages
    get_search_result_data(soup, links_to_explore)

    # Explore the product pages and get the links to the related products
    while len(links_to_explore) > 0 and deapth < 1:
        link = links_to_explore.pop(0)  # Get the first link from the list
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
    