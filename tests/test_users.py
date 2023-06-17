from rockr.db.models import users as usr
from rockr import settings

def test_get_user(): 
    users = usr.get_users()
    assert users is not None
    assert len(users) > 0
    assert "username" in users[0]
    assert "first_name" in users[0]
    assert "last_name" in users[0]
    assert isinstance(users[0]["username"], str)
    assert isinstance(users[0]["first_name"], str)
    assert isinstance(users[0]["last_name"], str)

def test_get_user_role(): 
    role = usr.get_user_role({"user_id": settings.AUTH0_USER_ID})
    assert role is not None
    assert len(role) == 1
    assert "description" in role[0]
    assert "id" in role[0]
    assert "name" in role[0]
    assert isinstance(role[0]["description"], str)
    assert isinstance(role[0]["id"], str)
    assert isinstance(role[0]["name"], str)
