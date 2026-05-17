from datetime import datetime, timezone
from extensions import db


class JWTBlocklist(db.Model):
    """Stores revoked JWT token identifiers (jti values)."""
    __tablename__ = 'jwt_blocklist'

    id         = db.Column(db.Integer, primary_key=True)
    jti        = db.Column(db.String(36), nullable=False, unique=True, index=True)
    revoked_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'<JWTBlocklist jti={self.jti}>'
