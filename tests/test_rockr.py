from flask_testing import TestCase
from rockr import create_app, db, settings, views
from flask import Flask
from rockr.queries import user_queries as uq
from rockr.models import User
import rockr.auth0.auth0_api_wrapper as auth0
import pytest

# The Child Man
TEST_USER_ID = 104
ADMIN_TEST_USER_ID = 1

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

TEST_EMAIL = "the_child_man@bluegrass.gov"

class MyTest(TestCase):

    def create_app(self):
        # pass in test configuration
        return create_app(test_config={
            "db_uri": settings.TEST_DATABASE_CONFIG
        })

    def setUp(self):
        self.test_user = self.get_test_user()
        self.admin_test_user = self.get_admin_test_user()
        self.api_wrapper = auth0.Auth0ApiWrapper()

    def get_admin_test_user(self):
        return db.session.execute(db.select(User).where(User.id == ADMIN_TEST_USER_ID)).scalars().all()[0]

    def get_test_user(self):
        return db.session.execute(db.select(User).where(User.id == TEST_USER_ID)).scalars().all()[0]
    
    def get_user_by_email(self, email):
        return db.session.execute(db.select(User).where(User.email == email)).scalars().all()[0]

    def test_get_users(self):
        users = uq.get_users()
        assert(users is not None)
        assert(len(users) > 0)

        assert "username" in users[0]
        assert "first_name" in users[0]
        assert "last_name" in users[0]
        assert "id" in users[0]
        assert "email" in users[0]
        assert "is_admin" in users[0]
        assert "is_active" in users[0]
        assert "is_band" in users[0]

        assert isinstance(users[0]["username"], str)
        assert isinstance(users[0]["first_name"], str)
        assert isinstance(users[0]["last_name"], str)
        assert isinstance(users[0]["id"], int)
        assert isinstance(users[0]["email"], str)
        assert isinstance(users[0]["is_admin"], bool)
        assert isinstance(users[0]["is_active"], bool)        
        assert isinstance(users[0]["is_band"], bool)

    def test_update_user_account(self):
        # "Poor man's deep copy"
        user_copy = self.test_user.serialize()

        # Change shit
        self.test_user.first_name = "Timmy T"
        self.test_user.last_name = "Childs"
        self.test_user.email = "ttchilders@msn.net"
        self.test_user.username = "ttchilds"
        self.test_user.is_admin = not self.test_user.is_admin
        self.test_user.is_active = not self.test_user.is_active
        self.test_user.is_band = not self.test_user.is_band
        users = [self.test_user.serialize()]
        uq.update_user_account(users)

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
        user = self.api_wrapper.get_users_by_email(self.test_user.email)[0]
        role = uq.get_user_role(user)[0]
        assert(role['name'] == 'Basic User')
        assert(role['description'] == 'Basic User')

    def test_admin_get_user_role(self):
        user = self.api_wrapper.get_users_by_email(self.admin_test_user.email)[0]
        role = uq.get_user_role(user)[0]
        assert(role['name'] == 'Admin')
        assert(role['description'] == 'Admin')   

    @pytest.mark.order(1)
    def test_create_user(self):
        uq.create_user_account(MOCK_USER)
        user = self.get_user_by_email(MOCK_USER['email'])
        assert(user.email == MOCK_USER['email'])
        assert(user.first_name == MOCK_USER['first_name'])
        assert(user.last_name == MOCK_USER['last_name'])
        assert(user.username == MOCK_USER['username'])
        assert(user.is_admin == MOCK_USER['is_admin'])
        assert(user.is_active == MOCK_USER['is_active'])
        assert(user.is_band == MOCK_USER['is_band'])

        res = self.api_wrapper.get_users_by_email(MOCK_USER['email'])
        assert len(res) == 1

    @pytest.mark.order(2)
    def test_get_user(self):
        data = uq.get_user(MOCK_USER["email"])["data"]
        assert 'id' in data
        assert 'email' in data
        assert 'username' in data
        assert 'first_name' in data
        assert 'last_name' in data
        assert 'is_admin' in data
        assert 'is_active' in data
        assert 'is_band' in data

        assert isinstance(data["id"], int)
        assert data["first_name"] == "Test"
        assert data["last_name"] ==  "ME"
        assert data["email"] == "testmebby@yahoooooo.com"
        assert data["username"] == ":)))))"
        assert data["is_admin"] == False
        assert data["is_active"] == False
        assert data["is_band"] == False

    @pytest.mark.order(3)
    def test_delete_user(self):
        user = self.get_user_by_email(MOCK_USER['email'])
        uq.delete_user_account(user.id, user.email)
        res = db.session.execute(db.select(User).where(User.email == MOCK_USER['email'])).scalars().all()
        assert len(res) == 0

        res = self.api_wrapper.get_users_by_email(MOCK_USER['email'])
        assert len(res) == 0

    def test_musical_interests(self):
        data = views.musical_interests()['data']
        assert data is not None
        assert len(data) > 0
        assert 'description' in data[0]
        assert 'id' in data[0]
        assert 'type' in data[0]
        assert isinstance(data[0]["description"], str)
        assert isinstance(data[0]["id"], int)        
        assert isinstance(data[0]["type"], str)

    def test_instruments(self):
        data = views.instruments()['data']
        assert data is not None
        assert len(data) > 0
        assert 'description' in data[0]
        assert 'id' in data[0]
        assert 'type' in data[0]
        assert isinstance(data[0]["description"], str)
        assert isinstance(data[0]["id"], int)        
        assert isinstance(data[0]["type"], str)

    def test_goals(self):
        data = views.goals()['data']
        assert data is not None
        assert len(data) > 0
        assert 'description' in data[0]
        assert 'id' in data[0]
        assert isinstance(data[0]["description"], str)
        assert isinstance(data[0]["id"], int)        

