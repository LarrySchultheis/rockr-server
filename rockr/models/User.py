from typing import Any
import rockr.auth0.auth0_api_wrapper as auth0
from sqlalchemy import select
from rockr import db
import json
from sqlalchemy_serializer import SerializerMixin


class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    pkid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    email = db.Column(db.String)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    is_band = db.Column(db.Boolean, default=False)


def conform_ret_arr(result_arr):
    ret_arr = []
    for r in result_arr:
        ret_arr.append(r.to_dict())
    return ret_arr

def get_users():
    users = db.session.execute(db.select(User)).scalars().all()
    return conform_ret_arr(users)

def update_user_account(users):
    for user in users:
        db.session.execute(db.update(User).where(User.pkid == user['pkid']).values(
            (
                user["pkid"],
                user["username"],
                user["first_name"],
                user["last_name"], 
                user["email"],
                user["is_admin"],
                user["is_active"],
                user["is_band"]
            )
        ))
    db.session.commit()
    return "success"


def delete_user_account(user_id):
    db.session.execute(db.delete(User).where(User.pkid == user_id))
    db.session.commit()
    return "success"

# Get user permission level from Auth0
def get_user_role(req):
    api_wrapper = auth0.Auth0ApiWrapper()
    return api_wrapper.get_user_role(req['user_id'])


def register_user():
    return ''


def create_users(data):
    return ''
