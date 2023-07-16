from flask import request, jsonify
from rockr import app, db_manager, db
from rockr.models import User
from rockr.queries.user_queries import conform_ret_arr
import rockr.queries.user_queries as uq
from rockr.models import (
    Instrument,
    Goal,
    MusicalInterest,
    UserMatch
)


def format_response(status, data):
    return {"status": status, "data": data}


def serialize_query_result(result):
    list_result = [r.serialize() for r in result]
    return jsonify(list_result).json

def serialize_tuple_list(result, keys):
    return_lst = []
    for r in result:
        obj = {}
        for i, t in enumerate(r):
            obj[keys[i]] = t.serialize()
        return_lst.append(obj)
    return jsonify(return_lst).json
            

@app.route('/', methods=["GET"])
def index():
    return "Welcome to Rockr!"

@app.route('/register', methods=['POST'])
def register():
    user = User(email=request.json["data"]["email"])
    db_manager.insert(user)
    return format_response(200, user.serialize())


@app.route('/get_users', methods=["GET"])
def get_users():
    data = uq.get_users()
    return format_response(200, data)


@app.route('/update_user_account', methods=["POST"])
def update_user_account():
    data = uq.update_user_account(request.json)
    return format_response(200, data)


@app.route('/user', methods=["GET"])
def user():
    resp = uq.get_user(request.args.get("email"))
    return format_response(resp["status"], resp["data"])


@app.route('/instrument', methods=["GET"])
def instruments():
    i = Instrument.query.all()
    return format_response(200, serialize_query_result(i))


@app.route('/goal', methods=["GET"])
def goals():
    g = Goal.query.all()
    return format_response(200, serialize_query_result(g))


@app.route('/musical_interest', methods=["GET"])
def musical_interests():
    mi = MusicalInterest.query.all()
    return format_response(200, serialize_query_result(mi))


@app.route('/create_user_account', methods=["POST"])
def create_user_account():
    data = uq.create_user_account(request.json)
    return format_response(200, data)


@app.route('/delete_user_account', methods=["GET"])
def delete_user_accout():
    data = uq.delete_user_account(request.args.get("id"), request.args.get("email"))
    return format_response(200, data)

@app.route('/change_password', methods=["POST"])
def change_password():
    resp = uq.change_password(request.json)
    return format_response(resp["status"], resp["data"])

# @app.route('/get_bands', methods=["GET"])
# def get_bands():
#     data = bands.get_bands()
#     return format_response(200, data)


@app.route('/get_user_role', methods=["POST"])
def get_user_role():
    data = uq.get_user_role(request.json)
    return format_response(200, data)

@app.route('/get_roles', methods=["GET"])
def get_roles():
    resp = uq.get_roles()
    return format_response(resp["status"], resp["data"])

@app.route('/matches', methods=["GET"])
def get_matches():
    user = User.query.filter_by(email=request.args.get("email")).first();
    matches = db.session.query(User, UserMatch).join(User, User.id == UserMatch.user_id).filter(UserMatch.match_id == user.id).all()
    return format_response(200, serialize_tuple_list(matches, ["user", "match"]))