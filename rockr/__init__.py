from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import URL
from flask_migrate import Migrate
from .settings import DATABASE_CONFIG
from flask_socketio import SocketIO
from flask_login import LoginManager
from rockr import settings

db = SQLAlchemy()
login_manager = LoginManager()
migrate = None

site_url = settings.PROD_SITE if settings.ENVIRIONMENT == "production" else settings.DEV_SITE

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    CORS(app, origins=[site_url])

    # configure the database
    if test_config is not None:
        url_object = URL.create(**test_config["db_uri"])
    else:
        url_object = URL.create(**DATABASE_CONFIG)
    app.config["SQLALCHEMY_DATABASE_URI"] = url_object
    db.init_app(app)
    with app.app_context():
        db.create_all()

    global migrate
    migrate = Migrate(app, db)

    return app


app = create_app()
login_manager.init_app(app)
login_manager.login_view = 'login'
app.secret_key = settings.FLASK_LOGIN_SECRET_KEY
socketio = SocketIO(app, cors_allowed_origins=[site_url])

# import here to avoid circular imports. Not a great practice, but docs say it's okay
import rockr.views
