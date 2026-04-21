from datetime import date as date_cls, datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from extensions import db
from models import SavedData

data_bp = Blueprint('data', __name__)


def _parse_date(value):
    """ Acceptera ISO-datum (YYYY-MM-DD) eller None. Returnerar date eller None. """
    if value is None or value == '':
        return None
    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except (TypeError, ValueError):
        return False  # markerar ogiltigt värde


@data_bp.route('/data', methods=['POST'])
@jwt_required()
def create_entry():
    """ Skapa en ny datapost (link, result, date). Inga relationer. """
    data = request.get_json() or {}
    link = data.get('link')
    result = data.get('result')
    date_value = data.get('date')

    # Obligatoriska fält
    if not link or result is None:
        return jsonify({'message': 'link och result krävs'}), 400

    # result ska vara numeriskt
    try:
        result = float(result)
    except (TypeError, ValueError):
        return jsonify({'message': 'result måste vara ett tal'}), 400

    # Datum – default till dagens datum om inget skickas in
    parsed_date = _parse_date(date_value)
    if parsed_date is False:
        return jsonify({'message': 'date måste vara i formatet YYYY-MM-DD'}), 400
    if parsed_date is None:
        parsed_date = date_cls.today()

    entry = SavedData(link=link, result=result, date=parsed_date)
    db.session.add(entry)
    db.session.commit()

    return jsonify(entry.to_dict()), 201


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

    if 'link' in data:
        if not data['link']:
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
