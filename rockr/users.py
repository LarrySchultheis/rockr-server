import rockr.db.rockr_db_manager as db
import rockr.auth0.auth0_api_wrapper as auth0


# Example EP to get users
def get_users():
    db_man = db.DbManager()
    cols = ['username', 'first_name', 'last_name'] 
    res = db_man.select('users', cols)
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