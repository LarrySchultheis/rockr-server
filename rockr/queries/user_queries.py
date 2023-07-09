from rockr import db
from rockr.models import User
import rockr.auth0.auth0_api_wrapper as auth0


def conform_ret_arr(result_arr):
    ret_arr = []
    for r in result_arr:
        ret_arr.append(r.serialize())
    return ret_arr


def get_users():
    users = db.session.execute(db.select(User)).scalars().all()
    return conform_ret_arr(users)


def get_user(email):
    user = db.session.execute(db.select(User).where(User.email == email)).scalars().all()[0]
    return {"status": 200, "data": user.serialize()}


def update_user_account(users):
    for user in users:
        db.session.execute(db.update(User).where(User.id == user['id']).values(
            (
                user["id"],
                user["email"],
                user["username"],
                user["first_name"],
                user["last_name"], 
                user["is_admin"],
                user["is_active"],
                user["is_band"]
            )
        ))
    db.session.commit()
    return "success"


def create_user_account(user):
    db.session.add(User(user))
    db.session.commit()
    create_auth0_account(user)
    # Add usr to auth0
    return "success"


def delete_user_account(user_id, email):
    db.session.execute(db.delete(User).where(User.id == user_id))
    db.session.commit()
    api_wrapper = auth0.Auth0ApiWrapper()
    api_wrapper.delete_auth0_account(email)
    return "success"

def change_password(user):
    api_wrapper = auth0.Auth0ApiWrapper()
    return api_wrapper.change_password(user)


def get_user_role(user):
    # get user permission level from Auth0
    api_wrapper = auth0.Auth0ApiWrapper()
    return api_wrapper.get_user_role(user['user_id'])

def get_roles():
    api_wrapper = auth0.Auth0ApiWrapper()
    return api_wrapper.get_roles()

def create_auth0_account(user):
    api_wrapper = auth0.Auth0ApiWrapper()
    return api_wrapper.create_auth0_account(user)
