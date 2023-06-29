from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import URL
from flask_migrate import Migrate
from .settings import DATABASE_CONFIG

db = SQLAlchemy()
migrate = None


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    CORS(app, origins=["http://localhost:3000"])

    # CITE: https://flask-sqlalchemy.palletsprojects.com/en/3.0.x/quickstart/
    # configure the database
    url_object = URL.create(**DATABASE_CONFIG)
    app.config["SQLALCHEMY_DATABASE_URI"] = url_object
    db.init_app(app)

    global migrate
    migrate = Migrate(app, db)

    return app


app = create_app()

# import here to avoid circular imports. Not a great practice, but docs say it's okay
import rockr.views
