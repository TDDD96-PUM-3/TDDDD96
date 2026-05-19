from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt
from datetime import timedelta
from extensions import db
from models import User, JWTBlocklist

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user account."""
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')

    # Validate required input fields.
    if not username or not password:
        return jsonify({'message': 'username och password krävs'}), 400

    # Ensure username uniqueness.
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'message': 'Användarnamnet är redan taget'}), 409

    # Persist the user.
    user = User(username=username, password=password)
    db.session.add(user)
    db.session.commit()

    return jsonify({
        'message': 'Användare skapad',
        'user': user.to_dict()
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate user credentials and issue an access token."""
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')

    # Validate required input fields.
    if not username or not password:
        return jsonify({'message': 'username och password krävs'}), 400

    # Look up user.
    user = User.query.filter_by(username=username).first()

    # Verify credentials.
    if not user or not user.check_password(password):
        return jsonify({'message': 'Fel användarnamn eller lösenord'}), 401

    # Identity is the user id, available via get_jwt_identity().
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
    """Log out by revoking the current token via JWT blocklist."""
    jti = get_jwt().get('jti')

    if jti:
        # Avoid duplicate rows if same token is logged out twice.
        already_revoked = JWTBlocklist.query.filter_by(jti=jti).first()
        if not already_revoked:
            db.session.add(JWTBlocklist(jti=jti))
            db.session.commit()

    return jsonify({'message': 'Utloggning lyckades'}), 200


def delete_user():
    pass
