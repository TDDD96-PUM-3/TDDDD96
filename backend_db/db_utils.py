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
    counterfeit_count = result.get('counterfeit')
    total_count = result.get('total')
    date_str = result.get('date')

    if not link or counterfeit_count is None:
        raise ValueError('link and result are required')

    try:
        counterfeit_val = float(counterfeit_count)
    except (TypeError, ValueError):
        raise ValueError('result must be a number')

    parsed_date = _parse_date(date_str)
    if parsed_date is False:
        raise ValueError('date must be in format YYYY-MM-DD')
    if parsed_date is None:
        parsed_date = date_cls.today()

    entry = SavedData(webname=webname, link=link, counterfeit_count=counterfeit_val,
                      tot_image_count=total_count, date=parsed_date)
    db.session.add(entry)
    db.session.commit()
    return entry


def build_stats_payload(entries):
    total_web = len(entries)
    flagged_web = sum(1 for entry in entries if entry.counterfeit_count > 0)
    total_img = sum(
        entry.tot_image_count for entry in entries if entry.tot_image_count)
    flagged_img = sum(entry.counterfeit_count for entry in entries)

    latest_entry = entries[0] if entries else None
    highest_entry = latest_entry
    for entry in entries:
        if highest_entry is None or entry.counterfeit_count > highest_entry.counterfeit_count:
            highest_entry = entry

    return {
        'found_counterfeits_tot_img': {
            'flagged_img': flagged_img,
            'total_img': total_img
        },
        'found_counterfeits_per_web': {
            'flagged_web': flagged_web,
            'total_web': total_web,
        },
        'result_from_prev_scrape': {
            'web_url': latest_entry.link if latest_entry else None,
            'webname': latest_entry.webname if latest_entry else None,
            'flagged_img': (
                latest_entry.counterfeit_count if latest_entry else None
            ),
            'total_img': (
                latest_entry.tot_image_count if latest_entry else None
            ),
        },
        'highest_flagged_count': {
            'web_url': highest_entry.link if highest_entry else None,
            'webname': highest_entry.webname if highest_entry else None,
            'flagged_img': (
                int(highest_entry.counterfeit_count)
                if highest_entry else None
            ),
            'total_img': (
                highest_entry.tot_image_count if highest_entry else None
            ),
        }
    }
