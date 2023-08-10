import json, urllib3, datetime
from rockr.models.auth0 import AuthToken
from rockr import settings, db
from password_generator import PasswordGenerator


class Auth0ApiWrapper:
    def __init__(self):
        self.settings = settings.AUTH0_PROD if settings.ENVIRIONMENT  == "production" else settings.AUTH0_DEV
        self.http = urllib3.PoolManager()
        self.token = AuthToken.query.filter_by(env=settings.ENVIRIONMENT).first()
        self.pw_gen = self._init_pw_gen()
        self._validate_token()

    def _init_pw_gen(self):
        pw_gen = PasswordGenerator()
        pw_gen.minlen = 10
        pw_gen.minuchars = 1
        pw_gen.minnumbers = 1
        pw_gen.minschars = 1

    # Don't want to test following two fxns since we only get 1000 tokens a month
    # RIP code coverage
    def _validate_token(self):
        if (
            datetime.datetime.now().timestamp()
            > self.token.granted_at + self.token.expires_in
        ):
            token_obj = self._refresh_api_token()
            self.token.token = token_obj["access_token"]
            self.token.expires_in = token_obj["expires_in"]
            self.token.granted_at = datetime.datetime.now().timestamp()
            self.token.env = settings.ENVIRIONMENT
            db.session.commit()

    def _refresh_api_token(self):
        resp = self.http.request(
            "POST",
            self.settings["token_url"],
            headers={"content-type": "application/json"},
            body=json.dumps(
                {
                    "client_id": self.settings["client_id"],
                    "client_secret": self.settings["client_secret"],
                    "audience": self.settings["auth0_url"],
                    "grant_type": "client_credentials",
                }
            ),
        )
        return json.loads(resp.data)

    def get_user_role(self, user_id):
        resp = self.http.request(
            "GET",
            f"{self.settings['auth0_url']}users/{user_id}/roles",
            headers={"Authorization": f"Bearer {self.token.token}"},
        )
        return json.loads(resp.data)

    def create_auth0_account(self, user):
        try:
            resp = self.http.request(
                "POST",
                f"{self.settings['auth0_url']}users",
                headers={
                    "Authorization": f"Bearer {self.token.token}",
                    "Content-type": "application/json",
                },
                body=json.dumps(
                    {
                        "email": user["email"],
                        "name": f"{user['first_name']} {user['last_name']}",
                        "verify_email": False,
                        "password": self.pw_gen.generate(),
                        "connection": "Username-Password-Authentication",
                    }
                ),
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
        except:
            print("An exception occurred")

    def _assign_admin(self, user, roles):
        user_id = user[0]["user_id"]
        role_id = [r["id"] for r in roles if r["name"] == "Admin"][0]
        resp = self.http.request(
            "POST",
            f"{self.settings['auth0_url']}users/{user_id}/roles",
            headers={
                "Authorization": f"Bearer {self.token.token}",
                "Content-type": "application/json",
            },
            body=json.dumps({"roles": [role_id]}),
        )
        return {"status": resp.status, "data": resp.data}

    def _assign_band(self, user, roles):
        user_id = user[0]["user_id"]
        role_id = [r["id"] for r in roles if r["name"] == "Band"][0]
        resp = self.http.request(
            "POST",
            f"{self.settings['auth0_url']}users/{user_id}/roles",
            headers={
                "Authorization": f"Bearer {self.token.token}",
                "Content-type": "application/json",
            },
            body=json.dumps({"roles": [role_id]}),
        )
        return {"status": resp.status, "data": resp.data}

    def _assign_basic_user(self, user, roles):
        user_id = user[0]["user_id"]
        role_id = [r["id"] for r in roles if r["name"] == "Basic User"][0]
        resp = self.http.request(
            "POST",
            f"{self.settings['auth0_url']}users/{user_id}/roles",
            headers={
                "Authorization": f"Bearer {self.token.token}",
                "Content-type": "application/json",
            },
            body=json.dumps({"roles": [role_id]}),
        )
        return {"status": resp.status, "data": resp.data}

    def get_roles(self):
        try:
            resp = self.http.request(
                "GET",
                f"{self.settings['auth0_url']}roles",
                headers={"Authorization": f"Bearer {self.token.token}"},
            )
            return {"status": resp.status, "data": json.loads(resp.data)}
        except:
            print("An exception occurred")

    def delete_auth0_account(self, email):
        try:
            user = self.get_users_by_email(email)[0]
            resp = self.http.request(
                "DELETE",
                f"{self.settings['auth0_url']}users/{user['user_id']}",
                headers={"Authorization": f"Bearer {self.token.token}"},
            )
            return resp.status
        except:
            print("An exception occurred")

    def get_users_by_email(self, email):
        try:
            resp = self.http.request(
                "GET",
                f"{self.settings['auth0_url']}users-by-email?email={email}",
                headers={"Authorization": f"Bearer {self.token.token}"},
            )
            return json.loads(resp.data)
        except:
            print("An exception occurred")

    # Keep just cause :)
    def change_password(self, user):
        try:
            user_id = self.get_users_by_email(user["email"])[0]["user_id"]
            resp = self.http.request(
                "PATCH",
                f"{self.settings['auth0_url']}users/{user_id}",
                headers={
                    "Authorization": f"Bearer {self.token.token}",
                    "Content-type": "application/json",
                },
                body=json.dumps({"password": user["password"]}),
            )
            return {"status": resp.status, "data": json.loads(resp.data)}
        except:
            print("An exception occurred")

    def reset_password(self, email):
        try:
            resp = self.http.request(
                "POST",
                f"{self.settings['password_reset_url']}",
                headers={
                    "Content-type": "application/json"
                },
                body=json.dumps({
                    "client_id": self.settings["client_id"],
                    "email": email,
                    "connection": "Username-Password-Authentication"
                })
            )
            return {"status": resp.status, "data": "success"}
        except:
            print("An exception occurred")