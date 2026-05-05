from flask import Blueprint, jsonify, request
from scrape_url_util import process_url_scrape
from flask_jwt_extended import jwt_required


backend_bp = Blueprint('backend', __name__)


@backend_bp.route('/scrape_url', methods=['GET'])
# @jwt_required()
def scrape_url():
    """ Endpoint to receive a URL from the frontend, scrape it, and return the data as JSON."""
    url = request.args.get('url', type=str)
    if not url:
        return jsonify({'error': 'Missing query parameter: url'}), 400
    try:
        result = process_url_scrape(url)
        return jsonify(result), 200
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400
    except Exception as exc:
        print(f"Error scraping URL {url}: {str(exc)}")
        return jsonify({'error': f'Server error: {str(exc)}'}), 500
