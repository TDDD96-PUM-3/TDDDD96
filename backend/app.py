from flask import Flask, jsonify, request
from universal_scraper import get_scraping_data


app = Flask(__name__)

# placeholder example route call


@app.route('/')
def hello_world():
    return 'Hello, World!'

# Route to recive frontend call, may change and further or differnt
# implementation may be needed. Currently uses args to get the url.


@app.route('/scrape_url', methods=['POST'])
def scrape_url():
    """ Endpoint to receive a URL from the frontend, scrape it, and return the data as JSON."""
    url = request.args.get('url', type=str)
    if not url:
        return jsonify({'error': 'Missing query parameter: url'}), 400

    data = get_scraping_data(url)
    if data is None:
        return jsonify({'error': 'Failed to scrape the URL'}), 400
    return jsonify(data), 200


def run_app():
    app.run(debug=True)


if __name__ == '__main__':
    run_app()
