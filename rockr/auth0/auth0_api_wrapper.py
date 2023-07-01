import json
import urllib3

from rockr import settings


class Auth0ApiWrapper():
    def __init__(self):
        self.settings = settings
        self.http = urllib3.PoolManager()

    def _get_api_token(self):
        # Will automate in future but for now just toss Auth0 Management API Token in settings.py
        return self.settings.API_TOKEN

    def get_user_role(self, user_id):
        token = self._get_api_token()
        resp = self.http.request(
                                    "GET",
                                    f"{self.settings.AUTH0_URL}/users/{user_id}/roles",
                                    headers={
                                        "Authorization": f"Bearer {token}"
                                    }
                                 )
        return json.loads(resp.data)
    
    def create_auth0_account(self, user):
        token = self._get_api_token()
        resp = self.http.request(
                                    "POST",
                                    f"{self.settings.AUTH0_URL}/users",
                                    headers={
                                        "Authorization": f"Bearer {token}",
                                        "Content-type": "application/json"
                                    },
                                    body=json.dumps({
                                        "email": user["email"],
                                        "name": f"{user['first_name']} {user['last_name']}",
                                        "verify_email": False,
                                        "password": user["password"],
                                        "connection": "Username-Password-Authentication"
                                    })
                                )
        return "success"
    
    def delete_auth0_account(self, email):
        token = self._get_api_token()
        user = self.get_users_by_email(email)[0]
        resp = self.http.request(
            "DELETE",
            f"{self.settings.AUTH0_URL}/users/{user['user_id']}",
            headers={
                "Authorization": f"Bearer {token}"
            }
        )
        return "success"
    
    def get_users_by_email(self, email):
        token = self._get_api_token()
        resp = self.http.request(
            "GET",
            f"{self.settings.AUTH0_URL}/users-by-email?email={email}",
            headers={
                "Authorization": f"Bearer {token}"
            })
        return json.loads(resp.data)
