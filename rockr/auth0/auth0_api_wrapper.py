import json, urllib3, datetime
from rockr.models.auth0 import AuthToken
from rockr import settings, db


class Auth0ApiWrapper():
    def __init__(self):
        self.settings = settings
        self.http = urllib3.PoolManager()
        self.token = AuthToken.query.all()[0]
        self._validate_token()
    
    # Don't want to test following two fxns since we only get 1000 tokens a month
    # RIP code coverage
    def _validate_token(self):
        if (datetime.datetime.now().timestamp() > self.token.granted_at + self.token.expires_in):
            token_obj = self._refresh_api_token()
            self.token.token = token_obj["access_token"]
            self.token.expires_in = token_obj["expires_in"]
            self.token.granted_at = datetime.datetime.now().timestamp()
            db.session.commit()

    def _refresh_api_token(self):
        resp = self.http.request(
            "POST",
            self.settings.TOKEN_URL,
            headers={"content-type": "application/json"},
            body=json.dumps({
                "client_id": self.settings.CLIENT_ID,
                "client_secret": self.settings.CLIENT_SECRET,
                "audience": self.settings.AUTH0_URL,
                "grant_type": "client_credentials"
            })
        )
        return json.loads(resp.data)

    def get_user_role(self, user_id):
        resp = self.http.request(
                                    "GET",
                                    f"{self.settings.AUTH0_URL}/users/{user_id}/roles",
                                    headers={
                                        "Authorization": f"Bearer {self.token.token}"
                                    }
                                 )
        return json.loads(resp.data)
    
    def create_auth0_account(self, user):
        resp = self.http.request(
                                    "POST",
                                    f"{self.settings.AUTH0_URL}users",
                                    headers={
                                        "Authorization": f"Bearer {self.token.token}",
                                        "Content-type": "application/json"
                                    },
                                    body=json.dumps({
                                        "email": user["email"],
                                        "name": f"{user['first_name']} {user['last_name']}",
                                        "verify_email": False,
                                        "password": user["password"],
                                        "connection": "Username-Password-Authentication",
                                    })
                                )
        auth0_user = self.get_users_by_email(user["email"])
        roles = self.get_roles()["data"]
        if user["is_admin"]:
            self._assign_admin(auth0_user, roles)
        else:
            self._assign_basic_user(auth0_user, roles)
        if user["is_band"]:
            self._assign_band(auth0_user, roles)
        return {"status": resp.status, "data": resp.data}
    
    def _assign_admin(self, user, roles):
        user_id = user[0]["user_id"]
        role_id = [r["id"] for r in roles if r["name"] == "Admin"][0]
        resp = self.http.request(
            "POST",
            f"{self.settings.AUTH0_URL}users/{user_id}/roles",
            headers={
                "Authorization": f"Bearer {self.token.token}",
                "Content-type": "application/json"
            },
            body=json.dumps({
                "roles": [
                    role_id
                ] 
            })
        )
        return {"status": resp.status, "data": resp.data}
    
    def _assign_band(self, user, roles):
        user_id = user[0]["user_id"]
        role_id = [r["id"] for r in roles if r["name"] == "Band"][0]
        resp = self.http.request(
            "POST",
            f"{self.settings.AUTH0_URL}users/{user_id}/roles",
            headers={
                "Authorization": f"Bearer {self.token.token}",
                "Content-type": "application/json"
            },
            body=json.dumps({
                "roles": [
                    role_id
                ] 
            })
        )
        return {"status": resp.status, "data": resp.data}
    
    def _assign_basic_user(self, user, roles):
        user_id = user[0]["user_id"]
        role_id = [r["id"] for r in roles if r["name"] == "Basic User"][0]
        resp = self.http.request(
            "POST",
            f"{self.settings.AUTH0_URL}users/{user_id}/roles",
            headers={
                "Authorization": f"Bearer {self.token.token}",
                "Content-type": "application/json"
            },
            body=json.dumps({
                "roles": [
                    role_id
                ] 
            })
        )
        return {"status": resp.status, "data": resp.data}

    def get_roles(self):
        resp = self.http.request(
            "GET",
            f"{self.settings.AUTH0_URL}roles",
            headers={
                "Authorization": f"Bearer {self.token.token}"
            }
        )
        return {"status": resp.status, "data": json.loads(resp.data)}
    
    def delete_auth0_account(self, email):
        user = self.get_users_by_email(email)[0]
        resp = self.http.request(
            "DELETE",
            f"{self.settings.AUTH0_URL}users/{user['user_id']}",
            headers={
                "Authorization": f"Bearer {self.token.token}"
            }
        )
        return resp.status
    
    def get_users_by_email(self, email):
        resp = self.http.request(
            "GET",
            f"{self.settings.AUTH0_URL}users-by-email?email={email}",
            headers={
                "Authorization": f"Bearer {self.token.token}"
            })
        return json.loads(resp.data)
    
    def change_password(self, user):
        user_id = self.get_users_by_email(user["email"])[0]["user_id"]
        resp = self.http.request(
            "PATCH",
            f"{self.settings.AUTH0_URL}users/{user_id}",
            headers={
                "Authorization": f"Bearer {self.token.token}",
                "Content-type": "application/json"
            },
            body=json.dumps({
                "password": user["password"]
            })
        )
        return {"status": resp.status, "data": json.loads(resp.data)}
