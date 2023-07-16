from flask_testing import TestCase
from rockr import create_app, db, settings, views, db_manager
from rockr.models import User, MusicalInterest, Instrument, Goal, UserMatch
import rockr.auth0.auth0_api_wrapper as auth0
import pytest, json
import jsonschema
from jsonschema import validate, RefResolver, Draft7Validator

# The Child Man
TEST_USER_ID = 202
ADMIN_TEST_USER_ID = 1

TEST_USER_AUTH0_ID = "auth0|647658e08c3b4001e6e0ae70"
ADMIN_USER_AUTH0_ID = "auth0|64a7fc38c8e7f423cb52858a"

MOCK_USER = {
    "first_name": "Test",
    "last_name":  "ME",
    "email": "testmebby@yahoooooo.com",
    "username": ":)))))",
    "password": "superW3akP@ssword",
    "is_admin": False,
    "is_active": False,
    "is_band": False
}

TEST_EMAIL = "the_child_man@ky.gov"

SCHEMA_PATH = "tests/schemas/"

def validate_json(jsonData, schema, resolver):
    try:
        validator = Draft7Validator(schema, resolver)
        validator.validate(jsonData)
    except jsonschema.exceptions.ValidationError as err:
        return False
    return True

def get_schema(schema_file):
    with open(schema_file, 'r') as fp:
        schema = json.load(fp)
        return schema

def get_schema_resolver(schema):
    return RefResolver.from_schema(schema)

class MyTest(TestCase):

    def create_app(self):
        # pass in test configuration
        return create_app(test_config={
            "db_uri": settings.TEST_DATABASE_CONFIG
        })[0]

    def setUp(self):
        self.test_user = self.get_test_user()
        self.admin_test_user = self.get_admin_test_user()
        self.api_wrapper = auth0.Auth0ApiWrapper()

    def get_admin_test_user(self):
        return User.query.get(ADMIN_TEST_USER_ID)

    def get_test_user(self):
        return User.query.get(TEST_USER_ID)
    
    def get_user_by_email(self, email):
        return User.query.filter_by(email=email).first()

    def test_get_users(self):
        users = User.query.all()
        assert(users is not None)
        assert(len(users) > 0)

        usr = users[0]
        assert isinstance(usr.username, str)
        assert isinstance(usr.first_name, str)
        assert isinstance(usr.last_name, str)
        assert isinstance(usr.id, int)
        assert isinstance(usr.email, str)
        assert isinstance(usr.is_admin, bool)
        assert isinstance(usr.is_active, bool)
        assert isinstance(usr.is_band, bool)

    def test_update_user_account(self):
        # "Poor man's deep copy"
        user_copy = self.test_user.serialize()

        # Change shit
        usr = User.query.get(TEST_USER_ID)
        usr.update(**{
            "first_name": "Timmy T",
            "last_name": "Childs",
            "email": "ttchilders@msn.net",
            "username": "ttchilds",
            "is_admin": not usr.is_admin,
            "is_active": not usr.is_active,
            "is_band": not usr.is_band,
        })

        # Assert shit
        updated_user = self.get_test_user()
        assert updated_user.first_name == "Timmy T"
        assert updated_user.last_name == "Childs"
        assert updated_user.email == "ttchilders@msn.net"
        assert updated_user.username == "ttchilds"
        assert updated_user.is_admin != user_copy["is_admin"]
        assert updated_user.is_active != user_copy['is_active']
        assert updated_user.is_band != user_copy['is_band']

        # Restore balance to the force
        self.test_user.first_name = user_copy["first_name"]
        self.test_user.last_name = user_copy["last_name"]
        self.test_user.email = user_copy["email"]
        self.test_user.username = user_copy["username"]
        self.test_user.is_admin = user_copy["is_admin"]
        self.test_user.is_active = user_copy["is_active"]
        self.test_user.is_band = user_copy["is_band"]
        db.session.commit()

    def test_get_user_role(self):
        api_wrapper = auth0.Auth0ApiWrapper()
        role = api_wrapper.get_user_role(TEST_USER_AUTH0_ID)[0]
        assert(role['name'] == 'Basic User')
        assert(role['description'] == 'Basic User')

    def test_admin_get_user_role(self):
        api_wrapper = auth0.Auth0ApiWrapper()
        role = api_wrapper.get_user_role(ADMIN_USER_AUTH0_ID)[0]
        assert(role['name'] == 'Admin')
        assert(role['description'] == 'Admin')   

    @pytest.mark.order(1)
    def test_create_user(self):
        db_manager.insert(User(MOCK_USER))
        user = User.query.filter_by(email=MOCK_USER["email"]).first()
        assert(user.email == MOCK_USER['email'])
        assert(user.first_name == MOCK_USER['first_name'])
        assert(user.last_name == MOCK_USER['last_name'])
        assert(user.username == MOCK_USER['username'])
        assert(user.is_admin == MOCK_USER['is_admin'])
        assert(user.is_active == MOCK_USER['is_active'])
        assert(user.is_band == MOCK_USER['is_band'])
        assert User.query.filter_by(email=MOCK_USER["email"]).count() == 1

    @pytest.mark.order(2)
    def test_get_user(self):
        usr = User.query.filter_by(email=MOCK_USER["email"]).first()

        assert isinstance(usr.id, int)
        assert usr.first_name == "Test"
        assert usr.last_name ==  "ME"
        assert usr.email == "testmebby@yahoooooo.com"
        assert usr.username == ":)))))"
        assert usr.is_admin == False
        assert usr.is_active == False
        assert usr.is_band == False

    @pytest.mark.order(3)
    def test_delete_user(self):
        usr = User.query.filter_by(email=MOCK_USER['email']).first()
        db_manager.delete(usr)
        assert User.query.filter_by(email=MOCK_USER['email']).count() == 0

    def test_musical_interests(self):
        mi_cnt = MusicalInterest.query.count()
        assert mi_cnt > 0

        mi = MusicalInterest.query.first()
        assert isinstance(mi.description, str)
        assert isinstance(mi.id, int)
        assert isinstance(mi.type, str)

    def test_instruments(self):
        i_cnt = Instrument.query.count()
        assert i_cnt > 0

        i = Instrument.query.first()
        assert isinstance(i.description, str)
        assert isinstance(i.id, int)
        assert isinstance(i.type, str)

    def test_goals(self):
        g_cnt = Goal.query.count()
        assert g_cnt > 0

        g = MusicalInterest.query.first()
        assert isinstance(g.description, str)
        assert isinstance(g.id, int)

    def test_matches(self):
        user = User.query.filter_by(email=TEST_EMAIL).first();
        matches = db.session.query(User, UserMatch).join(User, User.id == UserMatch.user_id).filter(UserMatch.match_id == user.id).all()
        assert len(matches) > 0
        matches_obj = views.serialize_tuple_list(matches, ["user", "match"])
        schema = get_schema(f"{SCHEMA_PATH}/user_match.schema.json")
        resolver = get_schema_resolver(schema)
        assert(validate_json(matches_obj, schema, resolver))
