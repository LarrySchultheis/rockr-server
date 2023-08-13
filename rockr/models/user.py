from rockr import db
from .mixins import SerializerMixin
from flask_login import UserMixin


class User(SerializerMixin, UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), unique=True, nullable=False)
    username = db.Column(db.String(32), unique=True)
    first_name = db.Column(db.String(128), nullable=True)
    last_name = db.Column(db.String(128), nullable=True)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    is_paused = db.Column(db.Boolean, default=False, nullable=False)
    is_band = db.Column(db.Boolean, default=False, nullable=False)
    is_active = db.Column(
        db.Boolean, default=True, nullable=False
    )  # tied to flask login
