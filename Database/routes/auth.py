from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt
from datetime import timedelta
from extensions import db
from models import User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    """ Registrera ny användare """
    # TODO: validera att username och password finns i requesten
    # TODO: kolla om användarnamnet redan är taget
    # TODO: skapa användaren och spara i databasen
    # TODO: returnera lämpligt svar
    pass


@auth_bp.route('/login', methods=['POST'])
def login():
    """ Logga in och få en JWT-token """
    # TODO: hämta username och password från requesten
    # TODO: hitta användaren i databasen
    # TODO: verifiera lösenordet med user.check_password()
    # TODO: skapa och returnera en access_token med create_access_token()
    pass


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """ Logga ut och invalidera token """
    # TODO: hämta jti från get_jwt() och lägg i JWTBlocklist
    pass