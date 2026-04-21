import mimetypes
import os
from io import BytesIO
from datetime import datetime
from urllib.parse import urlparse
from urllib.request import urlopen
import requests

MAX_IMAGE_BYTES = 10 * 1024 * 1024  # 10 MB
COPYCAT_API_CHECK_URL = os.getenv(
    'COPYCAT_API_CHECK_URL', 'http://copycat_api:3100/check')


def compose_result(url, result, websitename):
    """ Helper function to compose the result dictionary for saving to the database."""
    return {
        'name': websitename,
        'link': url,
        'counterfeit': result,
        'date': datetime.now().date()
    }


def send_to_db(result):
    pass


def get_copycat_result(image_urls):
    """Send scraped image URLs to Copycat API and return the first positive match.

    If no positive match is found, returns 'OK'.
    """
    if not image_urls:
        raise ValueError('No image URLs provided for model inference.')

    last_error = None
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
            successful_calls += 1
            prediction = response.json().get('prediction', 'OK')
            if prediction != 'OK':
                return prediction
        except Exception as exc:
            last_error = exc
            continue

    if last_error and successful_calls == 0:
        raise ValueError(
            f'Failed to run model inference: {last_error}') from last_error
    return 'OK'


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

    with urlopen(url, timeout=15) as response:
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
