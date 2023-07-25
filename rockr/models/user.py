from rockr import db
from .mixins import SerializerMixin


class User(SerializerMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), unique=True, nullable=False)
    username = db.Column(db.String(32), unique=True)
    first_name = db.Column(db.String(128), nullable=True)
    last_name = db.Column(db.String(128), nullable=True)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    is_paused = db.Column(db.Boolean, default=False, nullable=False)
    is_band = db.Column(db.Boolean, default=False, nullable=False)
    is_authenticated = db.Column(db.Boolean, default=False, nullable=False)
    is_active = db.Column(
        db.Boolean, default=False, nullable=False
    )  # tied to flask login
    is_anonymous = db.Column(db.Boolean, default=False, nullable=False)

    def __init__(self, user):
        self.username = user["username"]
        self.first_name = user["first_name"]
        self.last_name = user["last_name"]
        self.email = user["email"]
        self.is_admin = user["is_admin"]
        self.is_paused = user["is_paused"]
        self.is_band = user["is_band"]

    def get_id(self):
        return self.email
