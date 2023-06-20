import rockr.auth0.auth0_api_wrapper as auth0
from rockr import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    email = db.Column(db.String)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    is_band = db.Column(db.Boolean, default=False)


# Example EP to get users
def get_users():
    cols = ['username', 'first_name', 'last_name'] 
    res = db.select('users', cols)
    users = [{cols[0]: r[0], 
              cols[1]: r[1],
              cols[2]: r[2]} for r in res]
    return users


# Get user permission level from Auth0
def get_user_role(req):
    api_wrapper = auth0.Auth0ApiWrapper()
    return api_wrapper.get_user_role(req['user_id'])


def register_user():
    return ''


def create_users(data):
    return ''
