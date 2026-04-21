from extensions import db


class SavedData(db.Model):
    __tablename__ = 'saved_data'

    id         = db.Column(db.Integer, primary_key=True)
    link       = db.Column(db.String(200), nullable=False)
    result     = db.Column(db.Float, nullable=False)
    date       = db.Column(db.Date, nullable=False)

    # TODO: lägg till fler kolumner här efter behov, t.ex.:
    # category = db.Column(db.String(100))
    # is_public = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'id':      self.id,
            'link':    self.link,
            'result':  self.result,
            'date':    self.date.isoformat() if self.date else None,
        }