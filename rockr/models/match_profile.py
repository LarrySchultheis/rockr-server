from rockr import db
from .mixins import SerializerMixin
from .user import User


class MatchProfile(SerializerMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    bio = db.Column(db.Text, nullable=True)


class UserMatch(SerializerMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id),
                        nullable=False)  # user receiving the match
    match_id = db.Column(db.Integer, db.ForeignKey(User.id),
                         nullable=False)  # user that is the match
    accepted = db.Column(db.Boolean, default=False)
    seen = db.Column(db.Boolean, default=False)


class MusicalInterest(SerializerMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String, nullable=False)
    value = db.Column(db.String(128), nullable=False)


class UserMusicalInterest(SerializerMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    interest_id = db.Column(db.Integer, db.ForeignKey(MusicalInterest.id), nullable=False)


class Instrument(SerializerMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String, nullable=False)
    name = db.Column(db.String(128), nullable=False)


class UserInstrument(SerializerMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    instrument_id = db.Column(db.Integer, db.ForeignKey(Instrument.id), nullable=False)


class Goal(SerializerMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(256), nullable=False)


class UserGoal(SerializerMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    goal_id = db.Column(db.Integer, db.ForeignKey(Goal.id), nullable=False)
