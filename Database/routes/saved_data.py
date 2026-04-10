from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import SavedData, User

data_bp = Blueprint('data', __name__)


@data_bp.route('/data', methods=['POST'])
@jwt_required()
def create_entry():
    """ Skapa en ny datapost kopplad till inloggad användare """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'message': 'Användare hittades inte'}), 404

    data = request.get_json() or {}
    title = data.get('title')
    content = data.get('content')

    # Säkerställ att obligatoriska fält finns
    if not title or not content:
        return jsonify({'message': 'title och content krävs'}), 400

    entry = SavedData(user_id=user.id, title=title, content=content)
    db.session.add(entry)
    db.session.commit()

    return jsonify(entry.to_dict()), 201


@data_bp.route('/data', methods=['GET'])
@jwt_required()
def get_all_entries():
    """ Hämta alla dataposter för inloggad användare """
    user_id = get_jwt_identity()
    entries = SavedData.query.filter_by(user_id=user_id).order_by(
        SavedData.created_at.desc()).all()

    return jsonify([entry.to_dict() for entry in entries]), 200


@data_bp.route('/data/<int:entry_id>', methods=['GET'])
@jwt_required()
def get_entry(entry_id):
    """ Hämta en specifik datapost """
    user_id = get_jwt_identity()
    entry = SavedData.query.get(entry_id)

    if not entry:
        return jsonify({'message': 'Datapost hittades inte'}), 404

    # Kontrollera att posten tillhör inloggad användare
    if str(entry.user_id) != str(user_id):
        return jsonify({'message': 'Obehörig åtkomst'}), 403

    return jsonify(entry.to_dict()), 200


@data_bp.route('/data/<int:entry_id>', methods=['PUT'])
@jwt_required()
def update_entry(entry_id):
    """ Uppdatera en befintlig datapost """
    user_id = get_jwt_identity()
    entry = SavedData.query.get(entry_id)

    if not entry:
        return jsonify({'message': 'Datapost hittades inte'}), 404

    if str(entry.user_id) != str(user_id):
        return jsonify({'message': 'Obehörig åtkomst'}), 403

    data = request.get_json() or {}
    title = data.get('title')
    content = data.get('content')

    # Uppdatera endast de fält som skickats in
    if title is not None:
        entry.title = title
    if content is not None:
        entry.content = content

    db.session.commit()

    return jsonify(entry.to_dict()), 200


@data_bp.route('/data/<int:entry_id>', methods=['DELETE'])
@jwt_required()
def delete_entry(entry_id):
    """ Ta bort en datapost """
    user_id = get_jwt_identity()
    entry = SavedData.query.get(entry_id)

    if not entry:
        return jsonify({'message': 'Datapost hittades inte'}), 404

    if str(entry.user_id) != str(user_id):
        return jsonify({'message': 'Obehörig åtkomst'}), 403

    db.session.delete(entry)
    db.session.commit()

    return jsonify({'message': 'Datapost borttagen'}), 200
