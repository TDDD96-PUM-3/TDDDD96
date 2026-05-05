from extensions import db


class SavedData(db.Model):
    __tablename__ = 'saved_data'

    id = db.Column(db.Integer, primary_key=True)
    webname = db.Column(db.String(100), nullable=True)
    link = db.Column(db.String(200), nullable=False)
    counterfeit_count = db.Column(db.Float, nullable=False)
    tot_image_count = db.Column(db.Float, nullable=True)
    date = db.Column(db.Date, nullable=False)

    # TODO: lägg till fler kolumner här efter behov, t.ex.:
    # category = db.Column(db.String(100))
    # is_public = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'id':      self.id,
            'webname': self.webname,
            'link':    self.link,
            'counterfeit_count':  self.counterfeit_count,
            'tot_image_count': self.tot_image_count,
            'date':    self.date.isoformat() if self.date else None,
        }
