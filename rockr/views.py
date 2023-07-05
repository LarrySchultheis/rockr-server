from flask import request, jsonify
from rockr import app, db_manager
import rockr.auth0.auth0_api_wrapper as auth0
from rockr.models import User
import rockr.queries.user_queries as uq
from rockr.models import (
    Instrument,
    Goal,
    MusicalInterest,
)


def format_response(status, data):
    return {"status": status, "data": data}


def serialize_query_result(result):
    list_result = [r.serialize() for r in result]
    return jsonify(list_result).json


@app.route('/', methods=["GET"])
def index():
    return "Welcome to Rockr!"


# @app.route('/get_users', methods=["GET"])
# def get_users():
#     data = uq.get_users()
#     return format_response(200, data)


@app.route('/users/', defaults={'user_id': None})
@app.route('/users/<int:user_id>/')
def user(user_id=None):
    data = {}

    if request.method == "POST":
        # create
        usr = User(**request.form)
        db_manager.insert(usr)
    elif request.method == "PUT":
        # total update
        usr = User.query.get_or_404(user_id)
        # TODO
    elif request.method == "PATCH":
        # partial update
        usr = User.query.get_or_404(user_id)
        data = uq.update_user_account(request.json)
        # TODO
    elif request.method == "DELETE":
        usr = User.query.get_or_404(user_id)
        usr.delete()
        api_wrapper = auth0.Auth0ApiWrapper()
        api_wrapper.delete_auth0_account(usr.email)
    else:
        # GET
        if user_id:
            usr = User.query.get_or_404(user_id)
            data = usr.serialize()
        else:
            # get all
            usr_list = User.query.all()
            data = serialize_query_result(usr_list)

    return format_response(200, data)


@app.route('/instruments', methods=["GET"])
def instruments():
    i = Instrument.query.all()
    return format_response(200, serialize_query_result(i))


@app.route('/goals', methods=["GET"])
def goals():
    g = Goal.query.all()
    return format_response(200, serialize_query_result(g))


@app.route('/musical_interests', methods=["GET"])
def musical_interests():
    mi = MusicalInterest.query.all()
    return format_response(200, serialize_query_result(mi))


# @app.route('/update_user_account', methods=["POST"])
# def update_user_account():
#     data = uq.update_user_account(request.json)
#     return format_response(200, data)


# @app.route('/create_user_account', methods=["POST"])
# def create_user_account():
#     data = uq.create_user_account(request.json)
#     return format_response(200, data)


# @app.route('/delete_user_account', methods=["GET"])
# def delete_user_accout():
#     data = uq.delete_user_account(request.args.get("id"), request.args.get("email"))
#     return format_response(200, data)

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
