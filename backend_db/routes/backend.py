from flask import Blueprint, jsonify, request
from universal_scraper import get_scraping_data, build_driver
from backend_to_db import compose_result, send_to_db, get_copycat_result
from flask_jwt_extended import jwt_required


backend_bp = Blueprint('backend', __name__)


@backend_bp.route('/scrape_url', methods=['GET'])
# @jwt_required()
def scrape_url():
    """ Endpoint to receive a URL from the frontend, scrape it, and return the data as JSON."""
    url = request.args.get('url', type=str)
    if not url:
        return jsonify({'error': 'Missing query parameter: url'}), 400
    driver = build_driver()
    data = get_scraping_data(url, driver)
    if data is None:
        return jsonify({'error': 'Failed to scrape the URL'}), 400
    if not data.get('images'):
        return jsonify({'error': 'No images found on the target page'}), 400
    try:
        api_prob = get_copycat_result(data['images'])
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 500
    result = compose_result(url, api_prob, data['name'])
    send_to_db(result)
    return jsonify(result), 200
