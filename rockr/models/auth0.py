from rockr import db
from .mixins import SerializerMixin

class AuthToken(SerializerMixin, db.Model):
    __tablename__ = 'auth_token';
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.Text, nullable=False)
    expires_in = db.Column(db.Integer, nullable=False)
    granted_at = db.Column(db.Integer, nullable=False)

    def __init__(self, token_obj):
        self.token = token_obj["access_token"]
        self.expires_in = token_obj["expires_in"]
        self.granted_at = token_obj["granted_at"]