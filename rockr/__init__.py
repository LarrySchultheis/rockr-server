import os, json

from flask import Flask, request, jsonify
from flask_cors import CORS
from rockr import auth, users, bands

def format_response(status, data):
    return {"status": status, "data": data}

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    CORS(app)
    # Don't need below quite yet
    # app.config.from_mapping(
    #     SECRET_KEY='dev',
    #     # DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    # )

    # if test_config is None:
    #     # load the instance config, if it exists, when not testing
    #     app.config.from_pyfile('config.py', silent=True)
    # else:
    #     # load the test config if passed in
    #     app.config.from_mapping(test_config)

    # # ensure the instance folder exists
    # try:
    #     os.makedirs(app.instance_path)
    # except OSError:
    #     pass

    # Example routing scheme. Let's keep grouped functionality in dedicated python files.
    # This file should just be for kicking off logic based on http requests. Then our python files will 
    # call functions to complete logic and return a relevant response. This file should handle just
    # handle manipulating and routing

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

    @app.route('/register', methods =['POST'])
    def register():
        data = users.create_user(request.json)
        return format_response(200, data)

    @app.route('/getUsers', methods=["GET"])
    def getUsers():
        data = users.get_users()
        return format_response(200, data)

    @app.route('/getBands', methods=["GET"])
    def getBands():
        data = bands.get_bands()
        return format_response(200, data)
    
    @app.route('/getUserRole', methods=["POST"])
    def getUserRole():
        data = users.get_user_role(request.json)
        return format_response(200, data)
    return app