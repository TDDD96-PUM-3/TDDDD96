"""SQLAlchemy model for persisted scrape results."""

from extensions import db


class SavedData(db.Model):
    """Stores one scrape result with website and counterfeiting metadata."""
    __tablename__ = 'saved_data'

    id = db.Column(db.Integer, primary_key=True)
    webname = db.Column(db.String(100), nullable=True)
    link = db.Column(db.String(200), nullable=False)
    counterfeit_count = db.Column(db.Float, nullable=False)
    tot_image_count = db.Column(db.Float, nullable=True)
    date = db.Column(db.Date, nullable=False)

    # Add more optional columns here as project scope grows, e.g.:
    # category = db.Column(db.String(100))
    # is_public = db.Column(db.Boolean, default=False)

    def to_dict(self):
        """Serialize model fields for JSON API responses."""
        return {
            'id':      self.id,
            'webname': self.webname,
            'link':    self.link,
            'counterfeit_count':  self.counterfeit_count,
            'tot_image_count': self.tot_image_count,
            'date':    self.date.isoformat() if self.date else None,
        }
