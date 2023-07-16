from rockr import db
from .mixins import SerializerMixin
from .user import User


# a users contacts are all of their accepted matches
class UserMatch(SerializerMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    match_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    accepted = db.Column(db.Boolean, nullable=False)
    seen = db.Column(db.Boolean, nullable=False)