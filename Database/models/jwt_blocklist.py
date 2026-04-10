from extensions import db


class JWTBlocklist(db.Model):
    """
    Store revoked JWT tokens.

    Attributes:
        id: Primary key
        jti: JWT token identifier
    """
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String, nullable=False)  # JWT token identifier

    def __repr__(self):
        """Return string representation for debugging."""
        return f'<JWTBlocklist jti={self.jti}>'
