from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import SavedData, User

data_bp = Blueprint('data', __name__)


@data_bp.route('/data', methods=['POST'])
@jwt_required()
def create_entry():
    """ Skapa en ny datapost kopplad till inloggad användare """
    # TODO: hämta inloggad användare via get_jwt_identity()
    # TODO: validera att title och content finns i requesten
    # TODO: skapa ett SavedData-objekt och spara i databasen
    # TODO: returnera det skapade objektets to_dict()
    pass


@data_bp.route('/data', methods=['GET'])
@jwt_required()
def get_all_entries():
    """ Hämta alla dataposter för inloggad användare """
    # TODO: hämta inloggad användare via get_jwt_identity()
    # TODO: filtrera SavedData på user_id
    # TODO: returnera en lista med to_dict() för varje post
    pass


@data_bp.route('/data/<int:entry_id>', methods=['GET'])
@jwt_required()
def get_entry(entry_id):
    """ Hämta en specifik datapost """
    # TODO: hämta posten, returnera 404 om den inte finns
    # TODO: (valfritt) kontrollera att posten tillhör inloggad användare
    pass


@data_bp.route('/data/<int:entry_id>', methods=['PUT'])
@jwt_required()
def update_entry(entry_id):
    """ Uppdatera en befintlig datapost """
    # TODO: hämta posten, returnera 404 om den inte finns
    # TODO: verifiera att posten tillhör inloggad användare
    # TODO: uppdatera title och/eller content
    # TODO: spara och returnera uppdaterat objekt
    pass


@data_bp.route('/data/<int:entry_id>', methods=['DELETE'])
@jwt_required()
def delete_entry(entry_id):
    """ Ta bort en datapost """
    # TODO: hämta posten, returnera 404 om den inte finns
    # TODO: verifiera att posten tillhör inloggad användare
    # TODO: ta bort och returnera bekräftelse
    pass