from rockr import db
from .mixins import SerializerMixin
from .user import UserMatch


class MatchProfile(SerializerMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(UserMatch.id), nullable=False)
    bio = db.Column(db.Text, nullable=True)


class MusicalInterest(SerializerMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String, nullable=False)
    value = db.Column(db.String(128), nullable=False)


class Instrument(SerializerMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String, nullable=False)
    name = db.Column(db.String(128), nullable=False)


class Goal(SerializerMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(256), nullable=False)