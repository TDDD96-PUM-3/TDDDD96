import datetime
from datetime import datetime


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
