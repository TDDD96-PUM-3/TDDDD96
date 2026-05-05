import mimetypes
import os
from io import BytesIO
from datetime import datetime
from urllib.parse import urlparse
from urllib.request import urlopen, Request
import requests
from universal_scraper import get_scraping_data, build_driver
from db_utils import save_result_to_db

MAX_IMAGE_BYTES = 10 * 1024 * 1024
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
COPYCAT_API_CHECK_URL = os.getenv(
    'COPYCAT_API_CHECK_URL', 'http://localhost:3100/check')
FLASK_API_URL = os.getenv('FLASK_API_URL', 'http://localhost:8000')


def compose_result(url, result, websitename, products=None):
    """ Helper function to compose the result dictionary for saving to the database."""
    return {
        'name': websitename,
        'link': url,
        'counterfeit': result,
        'date': datetime.now().date().isoformat(),
        'products': products or []
        'date': datetime.now().date().isoformat(),
        'products': products or []
    }


def compose_result_frontend(websitename, url, flagged_images):
    """ Helper function to compose a result for sending to the frontend."""
    return {
        'name': websitename,
        'link': url,
        'flagged_images': [
            {
                'image_url': item['url'],
                'prediction': item.get('prediction')
            }
            for item in flagged_images
        ]
    }


def process_url_scrape(url):
    """Main function for scraping a URL, detects counterfeits
    and saves the result to the database. This function is called
    from scrape_url route.

    It scrapes the given URL, extracts all image URLs, and gets evaulated
    by the Ai API. The final result is composed and save to db.

    Args:
        url: The website URL to scrape

    Returns:
        dict: Result dictionary with keys: name, link, counterfeit, date
    """
    driver = build_driver()
    data = get_scraping_data(url, driver)

    if data is None:
        raise ValueError('Failed to scrape the URL')

    if not data.get('images'):
        raise ValueError('No images found on the target page')

    counterfeit_count, flagged_images = get_copycat_result(data['images'])

    products = get_copycat_result(data['images'], url, data['name'])
    counterfeit_count = sum(product['counterfeit'] for product in products)
    result = compose_result(url, counterfeit_count, data['name'], products)
    save_result_to_db({key: result[key]
                       for key in ('name', 'link', 'counterfeit', 'date')})

    result_db = compose_result_db(url, counterfeit_count, data['name'])
    save_result_to_db(result_db)

    frontend_result = {
        'name': result_db['name'],
        'link': result_db['link'],
        'flagged_images': [
            {
                'image_url': item['url'],
                'prediction': item.get('prediction')
            }
            for item in flagged_images
        ]
    }

    return frontend_result


def get_copycat_result(image_urls, page_url=None, website_name=None):
    """Send scraped image URLs to Copycat API and return one product result per image.
    """
    if not image_urls:
        raise ValueError('No image URLs provided for model inference.')
    last_error = None
    successful_calls = 0

    flagged_images = []

    products = []

    for index, image_url in enumerate(image_urls, start=1):
        try:
            filename, file_obj, content_type = img_url_to_file(image_url)
            response = requests.post(
                COPYCAT_API_CHECK_URL,
                files={'file': (filename, file_obj, content_type)},
                timeout=30,
            )
            response.raise_for_status()
            json_resp = response.json()
            prediction = json_resp.get('prediction', 'OK')
            successful_calls += 1

            if 'copyright_infringement_of_' in prediction:
                counterfeit_count += 1
                flagged_images.append(
                    {'url': image_url, 'prediction': prediction})

            is_counterfeit = 'copyright_infringement_of_' in prediction
            products.append({
                'id': index,
                'name': prediction.replace('copyright_infringement_of_', '') if is_counterfeit else f'{website_name or "Product"} image {index}',
                'link': page_url or image_url,
                'picture': image_url,
                'counterfeit': 1 if is_counterfeit else 0,
                'prediction': prediction,
            })

        except (ValueError, requests.RequestException) as exc:
            last_error = exc
            continue

    if last_error and successful_calls == 0:
        raise ValueError(
            f'Failed to run model inference: {last_error}') from last_error
    return products


def img_url_to_file(url, max_bytes=MAX_IMAGE_BYTES):
    """Download an image URL and return it as an in-memory file object.
    Returns a tuple: (filename, file_obj, content_type).
    The file_obj is a BytesIO instance ready for multipart uploads.
    Raises ValueError if the URL is invalid, doesn't point to an image,
    the image is empty, or exceeds max_bytes.
    """
    parsed_url = urlparse(url)
    if parsed_url.scheme not in ('http', 'https'):
        raise ValueError('URL must use http or https.')

    req = Request(url, headers={
                  'User-Agent': USER_AGENT})
    with urlopen(req, timeout=15) as response:
        content_type = response.headers.get_content_type()
        if not content_type.startswith('image/'):
            raise ValueError(
                f'URL does not point to an image. Got: {content_type}')

        image_bytes = response.read(max_bytes + 1)
        if not image_bytes:
            raise ValueError('Downloaded image is empty.')
        if len(image_bytes) > max_bytes:
            raise ValueError(
                f'Image exceeds maximum allowed size of {max_bytes / 1024 / 1024:.0f} MB.')

    filename = os.path.basename(parsed_url.path) or 'downloaded_image'
    if not os.path.splitext(filename)[1]:
        extension = mimetypes.guess_extension(content_type) or '.img'
        if extension == '.jpe':
            extension = '.jpg'
        filename = f'{filename}{extension}'

    file_obj = BytesIO(image_bytes)
    file_obj.name = filename
    file_obj.seek(0)
    return filename, file_obj, content_type
