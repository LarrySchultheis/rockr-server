import rockr.db.rockr_db_manager as db


# Example EP to get users
def get_users():
    db_man = db.DbManager()
    cols = ['username', 'first_name', 'last_name'] 
    res = db_man.select('users', cols)
    users = [{cols[0]: r[0], 
              cols[1]: r[1],
              cols[2]: r[2]} for r in res]
    return users

def register_user():
    return ''