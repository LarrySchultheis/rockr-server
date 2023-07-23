from flask import request, jsonify
from flask.views import MethodView
from sqlalchemy import func
from rockr import app, db_manager, db
from rockr.models import User, auth0
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


@app.route('/user_instruments/<int:user_id>', methods=["GET", "DELETE"])
def user_instruments(user_id):
    if request.method == "GET":
        ui = UserInstrument.query.filter_by(user_id=user_id)
        instruments = [Instrument.query.get(i.instrument_id) for i in ui]
        return format_response(200, serialize_query_result(instruments))
    elif request.method == "DELETE":
        ui = UserInstrument.query.filter_by(
            user_id=user_id,
            instrument_id=request.args["id"]
        ).first()
        db_manager.delete(ui)
        return format_response(204, None)


@app.route('/user_musical_interests/<int:user_id>', methods=["GET", "DELETE"])
def user_musical_interest(user_id):
    if request.method == "GET":
        umi = UserMusicalInterest.query.filter_by(user_id=user_id)
        interests = [MusicalInterest.query.get(i.interest_id) for i in umi]
        return format_response(200, serialize_query_result(interests))
    elif request.method == "DELETE":
        umi = UserMusicalInterest.query.filter_by(
            user_id=user_id,
            interest_id=request.args["id"]
        ).first()
        db_manager.delete(umi)
        return format_response(204, None)


@app.route('/user_goals/<int:user_id>', methods=["GET", "DELETE"])
def user_goals(user_id):
    if request.method == "GET":
        umi = UserGoal.query.filter_by(user_id=user_id)
        goals = [Goal.query.get(g.goal_id) for g in umi]
        return format_response(200, serialize_query_result(goals))
    else:
        ug = UserGoal.query.filter_by(
            user_id=user_id,
            goal_id=int(request.args["id"])
        ).first()
        db_manager.delete(ug)
        return format_response(204, None)
    
#Added for the User Band queries
@app.route('/user_band/<int:user_id>', methods=["GET","POST","DELETE"])
def user_band(user_id):
    if request.method == "GET":
        umi = UserBand.query.filter_by(user_id=user_id)
        bandsids = [Band.query.get(b.band_id) for b in umi]
        return format_response(200, serialize_query_result(bandsids))
    #For a new User Band Adding Query
    elif request.method == "POST":
        ub = UserBand.query(func.max(UserBand.id))
        highestid = ub.id;
        highestid = highestid+1;
        ubnew = {
            "id": highestid,
            "user_id": user_id,
            "band_id": int(request.args["id"])
        }
        db_manager.insert(ubnew)
        return format_response(201, None)
    else:
        ub = UserBand.query.filter_by(
            user_id=user_id,
            band_id=int(request.args["id"])
        ).first()
        db_manager.delete(ub)
        return format_response(204, None)
    
#In case you want to modify the functions to be like this
@app.route('/get_user_band/<int:user_id>', methods=["GET"])
def get_user_band(user_id):
    umi = UserBand.query.filter_by(user_id=user_id)
    bandsids = [Band.query.get(b.band_id) for b in umi]
    return format_response(200, serialize_query_result(bandsids))

@app.route('/add_user_band/<int:user_id>', methods=["POST"])
def add_user_band(user_id):
    #For a new User Band Adding Query
    ub = UserBand.query(func.max(UserBand.id))
    highestid = ub.id;
    highestid = highestid+1;
    ubnew = {
        "id": highestid,
        "user_id": user_id,
        "band_id": int(request.args["id"])
    }
    db_manager.insert(ubnew)
    return format_response(201, None)

@app.route('/remove_user_band/<int:user_id>', methods=["DELETE"])
def remove_user_band(user_id):
    ub = UserBand.query.filter_by(
        user_id=user_id,
        band_id=int(request.args["id"])
    ).first()
    db_manager.delete(ub)
    return format_response(204, None)

class ItemAPI(MethodView):
    init_every_request = False

    def __init__(self, model):
        self.model = model
        # self.validator = generate_validator(model)

    def _get_item(self, id):
        return self.model.query.get_or_404(id)

    def get(self, id):
        item = self._get_item(id)
        return jsonify(item.serialize())

    def patch(self, id):
        item = self._get_item(id)
        item.update(**request.json["params"])
        db.session.commit()
        return jsonify(item.serialize())

    def delete(self, id):
        item = self._get_item(id)
        db_manager.delete(item)
        return "", 204


class GroupAPI(MethodView):
    # list all data for
    init_every_request = False

    def __init__(self, model):
        self.model = model
        # self.validator = generate_validator(model, create=True)

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
    app.add_url_rule(f"/{name}/<int:id>", view_func=item)
    app.add_url_rule(f"/{name}/", view_func=group)


register_api(app, User, "users")
register_api(app, Instrument, "instruments")
register_api(app, Goal, "goals")
register_api(app, MusicalInterest, "musical_interests")

