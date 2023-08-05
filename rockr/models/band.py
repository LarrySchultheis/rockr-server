from rockr import db
from .mixins import SerializerMixin
from .user import User


# still not really sure that we need a Band model, but it's here for now
class Band(SerializerMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)


class UserBand(SerializerMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    band_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    is_accepted = db.Column(db.Boolean, default=False, nullable=False)
    seen = db.Column(db.Boolean, default=False, nullable=False)

