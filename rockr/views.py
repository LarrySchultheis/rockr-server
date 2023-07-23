import json
from flask import request, jsonify
from flask.views import MethodView
from sqlalchemy import func
from rockr import app, db_manager, db
from rockr.models import User, auth0, MatchProfile
import rockr.queries.user_queries as uq
import rockr.auth0.auth0_api_wrapper as auth0
from rockr.models import (
    Instrument,
    Goal,
    MusicalInterest,
    UserInstrument,
    UserGoal,
    UserMusicalInterest,
)
from rockr.models import User, auth0
from rockr.models.band import Band, UserBand

def format_response(status, data):
    return {"status": status, "data": data}


def serialize_query_result(result):
    list_result = [r.serialize() for r in result]
    return jsonify(list_result).json


@app.route('/', methods=["GET"])
def index():
    return "Welcome to Rockr!"


@app.route('/change_password', methods=["POST"])
def change_password():
    resp = uq.change_password(request.json)
    return format_response(resp["status"], resp["data"])


@app.route('/get_user_role', methods=["GET"])
def get_user_role():
    api_wrapper = auth0.Auth0ApiWrapper()
    data = {
        "role": api_wrapper.get_user_role(request.args["id"]),
        "user_obj": User.query.filter_by(email=request.args["email"]).first().serialize()
    }
    return jsonify(data)


@app.route('/get_roles', methods=["GET"])
def get_roles():
    resp = uq.get_roles()
    return format_response(resp["status"], resp["data"])


@app.route('/user_instruments/<int:user_id>', methods=["GET", "POST", "DELETE"])
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
            db_manager.insert(UserInstrument(user_id=user_id, instrument_id=instrument["id"]))
        return format_response(201, None)

    elif request.method == "DELETE":
        ui = UserInstrument.query.filter_by(
            user_id=user_id,
            instrument_id=request.args["id"]
        ).first()
        db_manager.delete(ui)
        return format_response(204, None)


@app.route('/user_musical_interests/<int:user_id>', methods=["GET", "POST", "DELETE"])
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
            db_manager.insert(UserMusicalInterest(user_id=user_id, interest_id=interest["id"]))
        return format_response(201, None)

    elif request.method == "DELETE":
        umi = UserMusicalInterest.query.filter_by(
            user_id=user_id,
            interest_id=request.args["id"]
        ).first()
        db_manager.delete(umi)
        return format_response(204, None)


@app.route('/user_goals/<int:user_id>', methods=["GET", "POST", "DELETE"])
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
            user_id=user_id,
            goal_id=int(request.args["id"])
        ).first()
        db_manager.delete(ug)
        return format_response(204, None)

@app.route('/user_band/<int:user_id>', methods=["GET","POST","DELETE"])
def user_band(user_id):
    if request.method == "GET":
        ub = UserBand.query.filter_by(user_id=user_id)
        bandsids = [Band.query.get(b.band_id) for b in ub]
        return format_response(200, serialize_query_result(bandsids))
    #For a new User Band Adding Query
    elif request.method == "POST":
        db_manager.insert(UserBand(user_id=user_id, band_id=request.args["id"]))
        return format_response(201, None)
    elif request.method == "DELETE":
        ub = UserBand.query.filter_by(
            user_id=user_id,
            band_id=int(request.args["id"])
        ).first()
        db_manager.delete(ub)
        return format_response(204, None)

@app.route('/check_match_profile/<int:user_id>', methods=["GET"])
def check_match_profile(user_id):
    if request.method == "GET":
        mp = MatchProfile.query.filter_by(user_id=user_id).first()
        if not mp:
            mp = MatchProfile(user_id=user_id)
            db_manager.insert(MatchProfile(user_id=user_id))
        return {"is_match_profile_complete": mp.is_complete}


class ItemAPI(MethodView):
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
        errors = self.validator.validate(request.json)

        if errors:
            return jsonify(errors), 400

        item = self.model.deserialize(request.json)
        db_manager.insert(item)
        return jsonify(item.serialize())


def register_api(app, model, name):
    item = ItemAPI.as_view(f"{name}-item", model)
    group = GroupAPI.as_view(f"{name}-group", model)
    app.add_url_rule(f"/{name}/<int:item_id>", view_func=item)
    app.add_url_rule(f"/{name}/", view_func=group)


register_api(app, User, "users")
register_api(app, Instrument, "instruments")
register_api(app, Goal, "goals")
register_api(app, MusicalInterest, "musical_interests")

