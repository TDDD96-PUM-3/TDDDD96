from models.jwt_blocklist import JWTBlocklist
from extensions import jwt
from flask import jsonify


@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload):
    """Return True when the token jti exists in the revocation blocklist."""
    jti = jwt_payload['jti']
    return JWTBlocklist.query.filter_by(jti=jti).first() is not None


@jwt.invalid_token_loader
def invalid_token_callback(reason):
    """Return a JSON error response for malformed or invalid tokens."""
    return jsonify({"status": "Fail", "message": reason}), 422


@jwt.unauthorized_loader
def missing_token_callback(reason):
    """Return a JSON error response when no JWT token is provided."""
    return jsonify({"status": "Fail", "message": reason}), 401


@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    """Return a JSON error response when a revoked token is used."""
    return jsonify({"status": "Fail", "message": "Token has been revoked"}), 401
