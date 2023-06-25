from flask import request
from rockr import auth, app, db_manager
from rockr.models import User


def format_response(status, data):
    return {"status": status, "data": data}


@app.route('/', methods=["GET"])
def index():
    return "Welcome to Rockr!"


@app.route('/login', methods=["POST"])
def login():
    data = auth.login(request.json)
    return format_response(200, data)


@app.route('/logout')
def logout():
    data = auth.logout(request.json)
    return format_response(200, data)


@app.route('/register', methods=['POST'])
def register():
    user = User(email=request.json["data"]["email"])
    db_manager.insert(user)
    return format_response(200, user.to_dict())


@app.route('/get_users', methods=["GET"])
def get_users():
    data = User.get_users()
    return format_response(200, data)


@app.route('/get_user_role', methods=["POST"])
def get_user_role():
    data = User.get_user_role(request.json)
    return format_response(200, data)
