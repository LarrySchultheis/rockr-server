import json
from flask import request, jsonify
from flask.views import MethodView
from flask_login import login_required, login_user, logout_user

from rockr import app, db_manager, db, socketio, login_manager
from rockr.utils import message_handler as mh
import rockr.queries.user_queries as uq
import rockr.auth0.auth0_api_wrapper as auth0_wrapper
from flask_socketio import emit
from rockr.models import (
    Goal,
    Instrument,
    MatchProfile,
    Message,
    MusicalInterest,
    User,
    UserBand,
    UserGoal,
    UserInstrument,
    UserMatch,
    UserMusicalInterest,
)

CURRENT_USER = None


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


# for PATCHing GroupAPI
def update_group(model_inst, **kwargs):
    for k, v in kwargs.items():
        if hasattr(model_inst, k):
            setattr(model_inst, k, v)


@app.route("/", methods=["GET"])
# @login_required
def index():
    return "Welcome to Rockr!"


@login_manager.user_loader
# @login_manager.request_loader
def load_user(user_email):
    global CURRENT_USER
    CURRENT_USER = User.query.filter_by(email=user_email).first()
    return CURRENT_USER


@login_manager.request_loader
def load_user_from_request(request):
    if CURRENT_USER:
        user = User.query.get(CURRENT_USER.id)
        if user:
            return user
    return None


@app.route("/login", methods=["GET"])
def login():
    if "email" in request.args.keys():
        usr = load_user(request.args["email"])
        success = login_user(usr)
        if success:
            return format_response(200, usr.serialize())
        else:
            return "error", 401


@app.route('/logout', methods=['POST'])
def logout():
    logout_user()
    return jsonify(**{'result': 200,
                      'data': {'message': 'logout success'}})


@app.route("/change_password", methods=["POST"])
# @login_required
def change_password():
    resp = uq.change_password(request.json)
    return format_response(resp["status"], resp["data"])


@app.route("/get_user_role", methods=["GET"])
def get_user_role():
    api_wrapper = auth0_wrapper.Auth0ApiWrapper()
    data = {
        "role": api_wrapper.get_user_role(request.args["id"])
    }
    return jsonify(data)


@app.route("/get_roles", methods=["GET"])
# @login_required
def get_roles():
    resp = uq.get_roles()
    return format_response(resp["status"], resp["data"])


@app.route("/matches", methods=["GET"])
# @login_required
def get_matches():
    user = User.query.filter_by(email=request.args.get("email")).first()
    matches = (
        db.session.query(User, UserMatch)
        .join(User, User.id == UserMatch.user_id)
        .filter(UserMatch.match_id == user.id)
        .all()
    )
    return format_response(200, serialize_tuple_list(matches, ["user", "match"]))


@app.route("/messages", methods=["GET"])
# @login_required
def get_messages():
    messages = Message.query.all()
    return format_response(200, serialize_query_result(messages))


@socketio.on("connect")
def test_connect():
    # print("connect")
    emit("after connect", {"data": "Lets dance"})


@socketio.on("message")
def handle_message(message):
    mh.save_message(message)
    emit(
        "messageResponse",
        {
            "data": message["text"],
            "sender": message["sender"],
            "recipient": message["recipient"],
        },
    )


@app.route("/user_instruments/<int:user_id>", methods=["GET", "POST", "DELETE"])
# @login_required
def user_instruments(user_id):
    if request.method == "GET":
        ui = UserInstrument.query.filter_by(user_id=user_id)
        instruments = [Instrument.query.get(i.instrument_id) for i in ui]
        return serialize_query_result(instruments)

    elif request.method == "POST":
        # delete all mappings for this user
        ui = UserInstrument.query.filter_by(user_id=user_id)
        for instrument in ui:
            db_manager.delete(instrument)
        # create new mappings from values in request
        for instrument in json.loads(request.data)["instruments"]:
            db_manager.insert(
                UserInstrument(user_id=user_id, instrument_id=instrument["id"])
            )
        return format_response(201, None)

    elif request.method == "DELETE":
        ui = UserInstrument.query.filter_by(
            user_id=user_id, instrument_id=request.args["id"]
        ).first()
        db_manager.delete(ui)
        return format_response(204, None)


@app.route("/user_musical_interests/<int:user_id>", methods=["GET", "POST", "DELETE"])
# @login_required
def user_musical_interest(user_id):
    if request.method == "GET":
        umi = UserMusicalInterest.query.filter_by(user_id=user_id)
        interests = [MusicalInterest.query.get(i.interest_id) for i in umi]
        return serialize_query_result(interests)

    elif request.method == "POST":
        # delete all mappings for this user
        umi = UserMusicalInterest.query.filter_by(user_id=user_id)
        for interest in umi:
            db_manager.delete(interest)
        # create new mappings from values in request
        for interest in json.loads(request.data)["interests"]:
            db_manager.insert(
                UserMusicalInterest(user_id=user_id, interest_id=interest["id"])
            )
        return format_response(201, None)

    elif request.method == "DELETE":
        umi = UserMusicalInterest.query.filter_by(
            user_id=user_id, interest_id=request.args["id"]
        ).first()
        db_manager.delete(umi)
        return format_response(204, None)


@app.route("/user_goals/<int:user_id>", methods=["GET", "POST", "DELETE"])
# @login_required
def user_goals(user_id):
    if request.method == "GET":
        umi = UserGoal.query.filter_by(user_id=user_id)
        goals = [Goal.query.get(g.goal_id) for g in umi]
        return serialize_query_result(goals)

    elif request.method == "POST":
        # delete all mappings for this user
        ug = UserGoal.query.filter_by(user_id=user_id)
        for goal in ug:
            db_manager.delete(goal)
        # create new mappings from values in request
        for goal in json.loads(request.data)["goals"]:
            db_manager.insert(UserGoal(user_id=user_id, goal_id=goal["id"]))
        return format_response(201, None)

    elif request.method == "DELETE":
        ug = UserGoal.query.filter_by(
            user_id=user_id, goal_id=int(request.args["id"])
        ).first()
        db_manager.delete(ug)
        return format_response(204, None)


@app.route("/user_band", methods=["GET"])
@app.route("/user_band/<int:band_id>", methods=["GET", "PATCH", "POST", "DELETE"])
# @login_required
def user_band(band_id=None):
    # a band is a user with is_band=True
    if request.method == "GET":
        # check for invitations for a user account
        if not band_id:
            user_id = request.args.get("user")
            band_invites = UserBand.query.filter_by(user_id=user_id, seen=False)
            return jsonify(serialize_query_result(band_invites))
        # get all band members for band account
        ub = UserBand.query.filter_by(band_id=band_id, is_accepted=True)
        bands_member_ids = [User.query.get(u.user_id) for u in ub]
        return format_response(200, serialize_query_result(bands_member_ids))

    elif request.method == "POST":
        user_query = UserBand.query.filter_by(band_id=band_id, user_id=request.json["params"]["user_id"])
        if user_query.count() == 0:
            ub = UserBand(band_id=band_id, user_id=request.json["params"]["user_id"])
            db_manager.insert(ub)
            return jsonify(ub.serialize())
        return jsonify(user_query.first().serialize())

    elif request.method == "PATCH":
        ub = UserBand.query.filter_by(band_id=band_id, user_id=request.json["params"]["user_id"]).first()
        ub.update(**request.json["params"])
        db.session.commit()
        return jsonify(ub.serialize())

    elif request.method == "DELETE":
        ub = UserBand.query.filter_by(
            band_id=band_id, user_id=int(request.args["user"])
        ).first()
        db_manager.delete(ub)
        return format_response(204, None)


@app.route("/user_matches/<int:user_id>", methods=["GET"])
# @login_required
def user_matches(user_id):
    matches = UserMatch.query.filter_by(user_id=user_id)
    match_users = [User.query.get(m.match_id) for m in matches]
    return serialize_query_result(match_users)


@app.route("/check_match_profile/<int:user_id>", methods=["GET"])
# @login_required
def check_match_profile(user_id):
    if request.method == "GET":
        mp = MatchProfile.query.filter_by(user_id=user_id).first()
        if not mp:
            mp = MatchProfile(user_id=user_id)
            db_manager.insert(MatchProfile(user_id=user_id))
        return {"is_match_profile_complete": mp.is_complete}


@app.route("/bands", methods=["GET"])
# @login_required
def bands():
    band_users = User.query.filter_by(is_band=True)
    band_users_dict = {b.id: b.serialize() for b in band_users}
    return jsonify(band_users_dict)


class ItemAPI(MethodView):
    decorators = [login_required]
    init_every_request = False

    def __init__(self, model):
        self.model = model

    def _get_item(self, item_id):
        return self.model.query.get_or_404(item_id)

    def get(self, item_id):
        item = self._get_item(item_id)
        return jsonify(item.serialize())

    def patch(self, item_id):
        item = self._get_item(item_id)
        item.update(**request.json["params"])
        db.session.commit()
        return jsonify(item.serialize())

    def delete(self, item_id):
        item = self._get_item(item_id)

        if isinstance(item, User):
            api_wrapper = auth0_wrapper.Auth0ApiWrapper()
            api_wrapper.delete_auth0_account(item.email)

        db_manager.delete(item)
        return "", 204


class GroupAPI(MethodView):
    init_every_request = False

    def __init__(self, model):
        self.model = model

    def get(self):
        items = self.model.query.all()
        return jsonify([item.serialize() for item in items])

    def post(self):
        item = self.model.deserialize(request.json)
        db_manager.insert(item)

        if isinstance(item, User):
            api_wrapper = auth0_wrapper.Auth0ApiWrapper()
            api_wrapper.create_auth0_account(item)

        return jsonify(item.serialize())

    def patch(self):
        resp = []
        items = json.loads(request.data)
        for item_dict in items:
            if "id" in item_dict.keys():
                obj = self.model.query.get(item_dict["id"])
                obj.update(**item_dict)
                db.session.commit()
                resp.append(self.model.query.get(item_dict["id"]))
        return serialize_query_result(resp)


def register_api(app, model, name):
    item = ItemAPI.as_view(f"{name}-item", model)
    group = GroupAPI.as_view(f"{name}-group", model)
    app.add_url_rule(f"/{name}/<int:item_id>", view_func=item)
    app.add_url_rule(f"/{name}/", view_func=group)


register_api(app, User, "users")
register_api(app, Instrument, "instruments")
register_api(app, Goal, "goals")
register_api(app, MusicalInterest, "musical_interests")
