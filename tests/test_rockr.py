from flask_testing import TestCase
from rockr import create_app, db, settings, db_manager, views
from rockr.models import (
    User,
    MusicalInterest,
    Instrument,
    Goal,
    UserInstrument,
    UserMusicalInterest,
    UserGoal,
    MatchProfile,
    UserMatch,
    UserBand,
    Message,
)
import rockr.auth0.auth0_api_wrapper as auth0
import rockr.analytics.match_algorithm as ma
import pytest

# The Child Man
TEST_USER_ID = 202
TEST_MATCH_ID = 5
ADMIN_TEST_USER_ID = 1

TEST_USER_AUTH0_ID = "auth0|647658e08c3b4001e6e0ae70"
ADMIN_USER_AUTH0_ID = "auth0|64a7fc38c8e7f423cb52858a"

MOCK_USER = {
    "first_name": "Test",
    "last_name": "ME",
    "email": "testmebby@yahoooooo.com",
    "username": ":)))))",
    "is_admin": False,
    "is_paused": False,
    "is_band": False,
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
        return User.query.get(ADMIN_TEST_USER_ID)

    def get_test_user(self):
        return User.query.get(TEST_USER_ID)

    def get_user_by_email(self, email):
        return User.query.filter_by(email=email).first()

    def test_get_users(self):
        users = User.query.all()
        assert users is not None
        assert len(users) > 0

        usr = users[0]
        assert isinstance(usr.username, str)
        assert isinstance(usr.first_name, str)
        assert isinstance(usr.last_name, str)
        assert isinstance(usr.id, int)
        assert isinstance(usr.email, str)
        assert isinstance(usr.is_admin, bool)
        assert isinstance(usr.is_paused, bool)
        assert isinstance(usr.is_band, bool)

    def test_update_user_account(self):
        # "Poor man's deep copy"
        user_copy = self.test_user.serialize()

        # Change shit
        usr = User.query.get(TEST_USER_ID)
        usr.update(
            **{
                "first_name": "Timmy T",
                "last_name": "Childs",
                "email": "ttchilders@msn.net",
                "username": "ttchilds",
                "is_admin": not usr.is_admin,
                "is_paused": not usr.is_paused,
                "is_band": not usr.is_band,
            }
        )

        # Assert shit
        updated_user = self.get_test_user()
        assert updated_user.first_name == "Timmy T"
        assert updated_user.last_name == "Childs"
        assert updated_user.email == "ttchilders@msn.net"
        assert updated_user.username == "ttchilds"
        assert updated_user.is_admin != user_copy["is_admin"]
        assert updated_user.is_paused != user_copy["is_paused"]
        assert updated_user.is_band != user_copy["is_band"]

        # Restore balance to the force
        self.test_user.first_name = user_copy["first_name"]
        self.test_user.last_name = user_copy["last_name"]
        self.test_user.email = user_copy["email"]
        self.test_user.username = user_copy["username"]
        self.test_user.is_admin = user_copy["is_admin"]
        self.test_user.is_paused = user_copy["is_paused"]
        self.test_user.is_band = user_copy["is_band"]
        db.session.commit()

    def test_get_user_role(self):
        role = self.api_wrapper.get_user_role(TEST_USER_AUTH0_ID)[0]
        assert role["name"] == "Basic User"
        assert role["description"] == "Basic User"

    def test_admin_get_user_role(self):
        role = self.api_wrapper.get_user_role(ADMIN_USER_AUTH0_ID)[0]
        assert role["name"] == "Admin"
        assert role["description"] == "Admin"

    def test_get_roles(self):
        roles = self.api_wrapper.get_roles()
        assert len(roles["data"]) == 3
        assert roles["status"] == 200
        role_names = [r["name"] for r in roles["data"]]
        assert "Admin" in role_names
        assert "Band" in role_names
        assert "Basic User" in role_names

    @pytest.mark.order(1)
    def test_create_user(self):
        db_manager.insert(User(**MOCK_USER))
        user = User.query.filter_by(email=MOCK_USER["email"]).first()
        assert user.email == MOCK_USER["email"]
        assert user.first_name == MOCK_USER["first_name"]
        assert user.last_name == MOCK_USER["last_name"]
        assert user.username == MOCK_USER["username"]
        assert user.is_admin == MOCK_USER["is_admin"]
        assert user.is_paused == MOCK_USER["is_paused"]
        assert user.is_band == MOCK_USER["is_band"]
        assert User.query.filter_by(email=MOCK_USER["email"]).count() == 1
        res = self.api_wrapper.create_auth0_account(MOCK_USER)
        assert res["status"] == 201


    @pytest.mark.order(2)
    def test_get_user(self):
        usr = User.query.filter_by(email=MOCK_USER["email"]).first()

        assert isinstance(usr.id, int)
        assert usr.first_name == "Test"
        assert usr.last_name == "ME"
        assert usr.email == "testmebby@yahoooooo.com"
        assert usr.username == ":)))))"
        assert not usr.is_admin
        assert not usr.is_paused
        assert not usr.is_band

    @pytest.mark.order(3)
    def test_get_user_by_email(self):
        res = self.api_wrapper.get_users_by_email(MOCK_USER["email"])[0]
        assert(res["email"] == MOCK_USER["email"])
        assert(res["name"]) == f'{MOCK_USER["first_name"]} {MOCK_USER["last_name"]}'

    @pytest.mark.order(4)
    def test_reset_password(self):
        res = self.api_wrapper.reset_password(MOCK_USER["email"])
        assert res["status"] == 200
        assert res["data"] == "success"

    @pytest.mark.order(5)
    def test_delete_user(self):
        usr = User.query.filter_by(email=MOCK_USER["email"]).first()
        db_manager.delete(usr)
        assert User.query.filter_by(email=MOCK_USER["email"]).count() == 0
        res = self.api_wrapper.delete_auth0_account(MOCK_USER["email"]);
        assert res == 204

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

    def test_messages(self):
        ct = Message.query.count()
        assert ct > 0

        m = Message.query.first()
        assert isinstance(m.id, int)
        assert isinstance(m.sender_id, int)
        assert isinstance(m.recipient_id, int)
        assert isinstance(m.message, str)

    def test_matches(self):
        ct = UserMatch.query.count()
        assert ct > 0

        m = UserMatch.query.first()
        assert isinstance(m.id, int)
        assert isinstance(m.user_id, int)
        assert isinstance(m.match_id, int)
        assert isinstance(m.accepted, bool)
        assert isinstance(m.seen, bool)

    def test_create_user_instruments(self):
        woodwind_instrument = Instrument.query.filter_by(type="woodwind").first()
        db_manager.insert(
            UserInstrument(user_id=TEST_USER_ID, instrument_id=woodwind_instrument.id)
        )
        assert UserInstrument.query.filter_by(user_id=TEST_USER_ID).count() > 0

        # mock response to user interacting with InstrumentSelect on FE
        for instrument in UserInstrument.query.filter_by(user_id=TEST_USER_ID):
            db_manager.delete(instrument)
        assert UserInstrument.query.filter_by(user_id=TEST_USER_ID).count() == 0

        brass_instruments = Instrument.query.filter_by(type="brass")
        for instrument in brass_instruments:
            db_manager.insert(
                UserInstrument(user_id=TEST_USER_ID, instrument_id=instrument.id)
            )
        assert (
            UserInstrument.query.filter_by(user_id=TEST_USER_ID).count()
            == brass_instruments.count()
        )

    def test_create_user_musical_interests(self):
        more_cowbell_bb = MusicalInterest.query.filter_by(
            description="more cowbell"
        ).first()
        db_manager.insert(
            UserMusicalInterest(user_id=TEST_USER_ID, interest_id=more_cowbell_bb.id)
        )
        assert UserMusicalInterest.query.filter_by(user_id=TEST_USER_ID).count() > 0

        # mock response to user interacting with InterestSelect on FE
        for interest in UserMusicalInterest.query.filter_by(user_id=TEST_USER_ID):
            db_manager.delete(interest)
        assert UserMusicalInterest.query.filter_by(user_id=TEST_USER_ID).count() == 0

        misc_interests = MusicalInterest.query.filter_by(type=None)
        for interest in misc_interests:
            db_manager.insert(
                UserMusicalInterest(user_id=TEST_USER_ID, interest_id=interest.id)
            )
        assert (
            UserMusicalInterest.query.filter_by(user_id=TEST_USER_ID).count()
            == misc_interests.count()
        )

    def test_create_user_goals(self):
        random_goal = Goal.query.filter().first()
        db_manager.insert(UserGoal(user_id=TEST_USER_ID, goal_id=random_goal.id))
        assert UserGoal.query.filter_by(user_id=TEST_USER_ID).count() > 0

        # mock response to user interacting with GoalSelect on FE
        for goal in UserGoal.query.filter_by(user_id=TEST_USER_ID):
            db_manager.delete(goal)
        assert UserGoal.query.filter_by(user_id=TEST_USER_ID).count() == 0

        band_goals = Goal.query.filter(Goal.description.contains("band"))
        for goal in band_goals:
            db_manager.insert(UserGoal(user_id=TEST_USER_ID, goal_id=goal.id))
        assert (
            UserGoal.query.filter_by(user_id=TEST_USER_ID).count() == band_goals.count()
        )

    def test_match_profile_check(self):
        usr = User.query.get(TEST_USER_ID)
        usr_mp = (
            MatchProfile.query.filter_by(user_id=usr.id).first()
            if MatchProfile.query.filter_by(user_id=usr.id).first()
            else db_manager.insert(MatchProfile(user_id=usr.id))
        )

        # destroy ye old match profile!
        for interest in UserMusicalInterest.query.filter_by(user_id=TEST_USER_ID):
            db_manager.delete(interest)
        assert UserMusicalInterest.query.filter_by(user_id=TEST_USER_ID).count() == 0

        for instrument in UserInstrument.query.filter_by(user_id=TEST_USER_ID):
            db_manager.delete(instrument)
        assert UserInstrument.query.filter_by(user_id=TEST_USER_ID).count() == 0

        for goal in UserGoal.query.filter_by(user_id=TEST_USER_ID):
            db_manager.delete(goal)
        assert UserGoal.query.filter_by(user_id=TEST_USER_ID).count() == 0
        assert not usr_mp.is_complete

        woodwind_instrument = Instrument.query.filter_by(type="woodwind").first()
        more_cowbell_bb = MusicalInterest.query.filter_by(
            description="more cowbell"
        ).first()
        random_goal = Goal.query.filter().first()

        db_manager.insert(
            UserInstrument(user_id=usr.id, instrument_id=woodwind_instrument.id)
        )
        assert not usr_mp.is_complete

        db_manager.insert(
            UserMusicalInterest(user_id=usr.id, interest_id=more_cowbell_bb.id)
        )
        assert not usr_mp.is_complete

        db_manager.insert(UserGoal(user_id=usr.id, goal_id=random_goal.id))
        assert usr_mp.is_complete

    def test_pause_user_account(self):
        usr = User.query.get(TEST_USER_ID)
        mock_patch_not_active = {"is_active": False}
        usr.update(**mock_patch_not_active)
        assert not usr.is_active

        mock_patch_is_active = {"is_active": True}
        usr.update(**mock_patch_is_active)
        assert usr.is_active

    def test_user_responds_to_match(self):
        usr = User.query.get(TEST_USER_ID)
        match = User.query.get(TEST_MATCH_ID)

        usr_match = UserMatch(user_id=usr.id, match_id=match.id)
        usr_match.accepted = True
        db.session.commit()
        assert usr_match.accepted

        usr_match.accepted = False
        db.session.commit()
        assert not usr_match.accepted

    def test_user_bands(self):
        assert UserBand.query.count() > 0
        
        b = UserBand.query.first()
        assert isinstance(b.id, int)
        assert isinstance(b.user_id, int)
        assert isinstance(b.band_id, int)
        assert isinstance(b.is_accepted, bool)
        assert isinstance(b.seen, bool)

    def test_band_users(self): 
        ub = UserBand.query.first()
        user = User.query.get(ub.user_id)
        assert isinstance(user, User)  
    
    def test_band_invites(self):
        assert UserBand.query.filter_by(seen=False).count() > 0
        band_invite = UserBand.query.filter_by(seen=False).first()
        user = User.query.get(band_invite.user_id)
        assert isinstance(user, User)
        assert band_invite.seen == False

    def test_bands(self):
        assert User.query.filter_by(is_band=True).count() > 0
        band_user = User.query.filter_by(is_band=True).first()
        assert isinstance(band_user, User)
        assert UserBand.query.filter_by(band_id=band_user.id).count() > 1
        band = UserBand.query.filter_by(band_id=band_user.id).first()
        assert isinstance(band, UserBand);

    def test_get_all_user_matches(self):
        matches = views.get_all_user_match_objects(1)
        for m in matches:
            assert m.accepted

    def test_format_response(self):
        res = views.format_response(200, "Test")
        assert "status" in res.keys()
        assert "data" in res.keys()
        assert res["status"] == 200
        assert res["data"] == "Test"      

    def test_messages(self):
        msg_ct = Message.query.count()
        messages = Message.query.order_by(Message.ts.asc()).all()
        assert len(messages) == msg_ct
        for m in messages:
            assert isinstance(m, Message)

    def test_match_algorithm(self):
        res = ma.match_algorithm(ADMIN_TEST_USER_ID)
        for r in res:
            assert isinstance(r[0], UserMatch)
            assert isinstance(r[1], float)