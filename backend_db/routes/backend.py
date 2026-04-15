from flask import Blueprint, jsonify, request
from universal_scraper import get_scraping_data, build_driver

backend_bp = Blueprint('backend', __name__)


@backend_bp.route('/scrape', methods=['GET'])
def scrape_url():
    """ Endpoint to receive a URL from the frontend, scrape it, and return the data as JSON."""
    url = request.args.get('url', type=str)
    if not url:
        return jsonify({'error': 'Missing query parameter: url'}), 400
    driver = build_driver()
    data = get_scraping_data(url, driver)
    if data is None:
        return jsonify({'error': 'Failed to scrape the URL'}), 400
    return jsonify(data), 200
