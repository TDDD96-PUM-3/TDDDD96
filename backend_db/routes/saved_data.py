from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from extensions import db
from models import SavedData
from db_utils import save_result_to_db, _parse_date

data_bp = Blueprint('data', __name__)


@data_bp.route('/data', methods=['POST'])
@jwt_required()
def create_entry():
    """ Creates a new data entry from endpoint. Expects JSON
    with fields: webname, url, result, date (YYYY-MM-DD). """
    data = request.get_json()
    result = {
        'name': data.get('webname'),
        'link': data.get('url'),
        'counterfeit': data.get('result'),
        'date': data.get('date')
    }
    try:
        save_result_to_db(result)
        return jsonify({'message': 'Data entry succesfully created'}), 201
    except ValueError as exc:
        return jsonify({'message': str(exc)}), 400


@data_bp.route('/data', methods=['GET'])
@jwt_required()
def get_all_entries():
    """ Hämta alla dataposter (ingen filtrering per användare). """
    entries = SavedData.query.order_by(SavedData.date.desc()).all()
    return jsonify([entry.to_dict() for entry in entries]), 200


@data_bp.route('/data/<int:entry_id>', methods=['GET'])
@jwt_required()
def get_entry(entry_id):
    """ Hämta en specifik datapost. """
    entry = SavedData.query.get(entry_id)
    if not entry:
        return jsonify({'message': 'Datapost hittades inte'}), 404
    return jsonify(entry.to_dict()), 200


@data_bp.route('/data/<int:entry_id>', methods=['PUT'])
@jwt_required()
def update_entry(entry_id):
    """ Uppdatera en befintlig datapost. Endast skickade fält uppdateras. """
    entry = SavedData.query.get(entry_id)
    if not entry:
        return jsonify({'message': 'Datapost hittades inte'}), 404

    data = request.get_json() or {}

    if 'webname' in data:
        if not data['webname']:
            return jsonify({'message': 'webname får inte vara tomt'}), 400
        entry.webname = data['webname']
    if 'link' in data:
        if not data['url']:
            return jsonify({'message': 'link får inte vara tomt'}), 400
        entry.link = data['link']

    if 'result' in data:
        try:
            entry.result = float(data['result'])
        except (TypeError, ValueError):
            return jsonify({'message': 'result måste vara ett tal'}), 400

    if 'date' in data:
        parsed_date = _parse_date(data['date'])
        if parsed_date is False or parsed_date is None:
            return jsonify({'message': 'date måste vara i formatet YYYY-MM-DD'}), 400
        entry.date = parsed_date

    db.session.commit()
    return jsonify(entry.to_dict()), 200


@data_bp.route('/data/<int:entry_id>', methods=['DELETE'])
@jwt_required()
def delete_entry(entry_id):
    """ Ta bort en datapost. """
    entry = SavedData.query.get(entry_id)
    if not entry:
        return jsonify({'message': 'Datapost hittades inte'}), 404

    db.session.delete(entry)
    db.session.commit()
    return jsonify({'message': 'Datapost borttagen'}), 200


@data_bp.route('/data/stats', methods=['GET'])
def get_stats():
    """Gather stats for the stats page piecharts."""
    entries = SavedData.query.order_by(
        SavedData.date.desc(), SavedData.id.desc()
    ).all()

    total_web = len(entries)
    flagged_web = 1
    flagged_img = 1

    latest_entry = 2
    highest_entry = 3

    return jsonify({
        'found_counterfeits_tot_img': {
            'flagged_img': flagged_img,
            'total_img': None,  # placehold
        },
        'found_counterfeits_per_web': {
            'flagged_web': flagged_web,
            'total_web': total_web,
        },
        'result_from_prev_scrape': (
            {
                'web_url': latest_entry.link,
                'webname': latest_entry.webname,
                'flagged_img': int(latest_entry.result or 0),
                'total_img': None,
            }
            if latest_entry else None
        ),
        'highest_flagged_percentage': (
            {
                'web_url': highest_entry.link,
                'webname': highest_entry.webname,
                'flagged_img': int(highest_entry.result or 0),
                'total_img': None,
                'flagged_percentage': None,
            }
            if highest_entry else None
        )
    }), 200
