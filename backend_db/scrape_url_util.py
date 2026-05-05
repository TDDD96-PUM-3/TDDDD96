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


def compose_result(url, result, websitename):
    """ Helper function to compose the result dictionary for saving to the database."""
    return {
        'name': websitename,
        'link': url,
        'counterfeit': result,
        'date': datetime.now().date().isoformat()
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

    counterfeit_count = get_copycat_result(data['images'])
    result = compose_result(url, counterfeit_count, data['name'])
    save_result_to_db(result)

    return result


def get_copycat_result(image_urls):
    """Send scraped image URLs to Copycat API and return amount of counterfeit images detected
    on a website url. Has some error handling.
    """
    if not image_urls:
        raise ValueError('No image URLs provided for model inference.')
    last_error = None
    counterfeit_count = 0
    successful_calls = 0

    for image_url in image_urls:
        try:
            filename, file_obj, content_type = img_url_to_file(image_url)
            response = requests.post(
                COPYCAT_API_CHECK_URL,
                files={'file': (filename, file_obj, content_type)},
                timeout=30,
            )
            response.raise_for_status()
            prediction = response.json().get('prediction', 'OK')
            successful_calls += 1
            if 'copyright_infringement_of_' in prediction:
                counterfeit_count += 1
        except (ValueError, requests.RequestException) as exc:
            last_error = exc
            continue

    if last_error and successful_calls == 0:
        raise ValueError(
            f'Failed to run model inference: {last_error}') from last_error
    return counterfeit_count


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
