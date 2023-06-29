import rockr.auth0.auth0_api_wrapper as auth0
from rockr import db
from .mixins import SerializerMixin
from .match_profile import Goal


class User(SerializerMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), unique=True, nullable=False)
    username = db.Column(db.String(32), unique=True)
    first_name = db.Column(db.String(128), nullable=True)
    last_name = db.Column(db.String(128), nullable=True)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    is_band = db.Column(db.Boolean, default=False)

    @property
    def user_role(self):
        # get user permission level from Auth0
        # this acts like a property and can be accessed like user.user_role
        api_wrapper = auth0.Auth0ApiWrapper()
        return api_wrapper.get_user_role(self.id)


class UserMatch(SerializerMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('public.user.id'),
                        nullable=False)  # user receiving the match
    match_id = db.Column(db.Integer, db.ForeignKey('public.user.id'),
                         nullable=False)  # user that is the match
    accepted = db.Column(db.Boolean, default=False)
    seen = db.Column(db.Boolean, default=False)


class UserMusicalInterest(SerializerMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('public.user.id'), nullable=False)
    interest_id = db.Column(db.Integer, db.ForeignKey('public.musicalinterest.id'), nullable=False)


class UserInstrument(SerializerMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('public.user.id'), nullable=False)
    instrument_id = db.Column(db.Integer, db.ForeignKey('public.instrument.id'), nullable=False)


class UserGoal(SerializerMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    goal_id = db.Column(db.Integer, db.ForeignKey(Goal.id), nullable=False)
