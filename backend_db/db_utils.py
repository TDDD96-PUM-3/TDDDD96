from datetime import datetime, date as date_cls
from extensions import db
from models import SavedData


def _parse_date(value):
    if value is None or value == '':
        return None
    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except (TypeError, ValueError):
        return False


def save_result_to_db(result):
    """Saves a result dictionary to the database after some validations.
    Expects a dictionary with keys: name, link, counterfeit, date.
    """
    webname = result.get('name')
    link = result.get('link')
    counterfeit = result.get('counterfeit')
    date_str = result.get('date')

    if not link or counterfeit is None:
        raise ValueError('link and result are required')

    try:
        counterfeit_val = float(counterfeit)
    except (TypeError, ValueError):
        raise ValueError('result must be a number')

    parsed_date = _parse_date(date_str)
    if parsed_date is False:
        raise ValueError('date must be in format YYYY-MM-DD')
    if parsed_date is None:
        parsed_date = date_cls.today()

    entry = SavedData(webname=webname, link=link,
                      result=counterfeit_val, date=parsed_date)
    db.session.add(entry)
    db.session.commit()
    return entry
