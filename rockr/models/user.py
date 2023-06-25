import rockr.auth0.auth0_api_wrapper as auth0
from rockr import db
from .mixins import SerializerMixin


class User(SerializerMixin, db.Model):
    pkid = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)
    username = db.Column(db.String, unique=True)
    first_name = db.Column(db.String, nullable=True)
    last_name = db.Column(db.String, nullable=True)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    is_band = db.Column(db.Boolean, default=False)

    __tablename__ = "users"

    @property
    def user_role(self):
        # get user permission level from Auth0
        # this acts like a property and can be accessed like user.user_role
        api_wrapper = auth0.Auth0ApiWrapper()
        return api_wrapper.get_user_role(self.id)
