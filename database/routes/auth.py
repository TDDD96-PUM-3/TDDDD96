from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt
from datetime import timedelta
from extensions import db
from models import User

auth_bp = Blueprint('auth', __name__)


JWT_BLOCKLIST = set()


@auth_bp.route('/register', methods=['POST'])
def register():
    """ Registrera ny användare """
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')

    # Validera att nödvändiga fält finns
    if not username or not password:
        return jsonify({'message': 'username och password krävs'}), 400

    # Kontrollera om användarnamnet redan finns
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'message': 'Användarnamnet är redan taget'}), 409

    # Skapa och spara användaren
    user = User(username=username, password=password)
    db.session.add(user)
    db.session.commit()

    return jsonify({
        'message': 'Användare skapad',
        'user': user.to_dict()
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """ Logga in och få en JWT-token """
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')

    # Kontrollera att båda fälten skickats med
    if not username or not password:
        return jsonify({'message': 'username och password krävs'}), 400

    # Hitta användaren i databasen
    user = User.query.filter_by(username=username).first()

    # Verifiera användare och lösenord
    if not user or not user.check_password(password):
        return jsonify({'message': 'Fel användarnamn eller lösenord'}), 401

    # JWT-identiteten sätts till användarens id så att den enkelt kan hämtas
    # via get_jwt_identity() i skyddade routes.
    access_token = create_access_token(
        identity=str(user.id),
        expires_delta=timedelta(hours=1)
    )

    return jsonify({
        'message': 'Inloggning lyckades',
        'access_token': access_token,
        'user': user.to_dict()
    }), 200


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """ Logga ut och invalidera token """
    jwt_data = get_jwt()
    jti = jwt_data.get('jti')

    # Lägg token-id i blocklist så att den kan spärras.
    # Detta är en enkel lösning som håller sig inom befintlig struktur.
    if jti:
        JWT_BLOCKLIST.add(jti)

    return jsonify({'message': 'Utloggning lyckades'}), 200


def delete_user():
