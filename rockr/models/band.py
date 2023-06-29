from rockr import db
from .mixins import SerializerMixin


# still not really sure that we need a Band model, but it's here for now
class Band(SerializerMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, length=128, nullable=False)


class UserBand(SerializerMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('public.user.id'), nullable=False)
    band_id = db.Column(db.Integer, db.ForeignKey('public.band.id'), nullable=False)
