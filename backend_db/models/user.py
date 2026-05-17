"""User model with password hashing and serialization helpers."""

from extensions import db, bcrypt
from datetime import datetime, timezone


def _utcnow():
    """Return timezone-aware UTC timestamp for model defaults."""
    return datetime.now(timezone.utc)


class User(db.Model):
    """Application user account model."""
    __tablename__ = 'user'

    id         = db.Column(db.Integer, primary_key=True)
    username   = db.Column(db.String(80), unique=True, nullable=False)
    password   = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=_utcnow)

    def __init__(self, username, password):
        self.username = username
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password) -> bool:
        """Verify plaintext password against stored bcrypt hash."""
        return bcrypt.check_password_hash(self.password, password)

    def to_dict(self):
        """Serialize safe user fields for API responses."""
        return {
            'id':         self.id,
            'username':   self.username,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            # Extend with more safe fields here if needed.
        }