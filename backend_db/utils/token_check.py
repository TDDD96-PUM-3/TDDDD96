from models.jwt_blocklist import JWTBlocklist
from extensions import jwt
from flask import jsonify


def check_if_token_is_revoked(jwt_header, jwt_payload):
    """
    Check if a JWT token is revoked.

    Args:
        jwt_header: JWT header (ignored)
        jwt_payload: JWT payload

    Returns:
        True if token is in blocklist, False otherwise
    """
    jti = jwt_payload['jti']  # Unique JWT identifier
    return JWTBlocklist.query.filter_by(jti=jti).first() is not None


@jwt.invalid_token_loader
def invalid_token_callback(reason):
    """
    Callback for invalid JWT tokens.
    Returns JSON response with status 422.
    """
    print("Invalid token reason:", reason)  # Debug
    return jsonify({"status": "Fail", "message": reason}), 422


@jwt.unauthorized_loader
def missing_token_callback(reason):
    """
    Callback for requests without JWT token.
    Returns JSON response with status 401.
    """
    print("Missing token reason:", reason)  # Debug
    return jsonify({"status": "Fail", "message": reason}), 401


@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    """
    Callback for revoked JWT tokens.
    Returns JSON response with status 401.
    """
    print("Revoked token payload:", jwt_payload)  # Debug
    return jsonify({"status": "Fail", "message": "Token has been revoked"}), 401
