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
        resp = self.http.request("GET",
                                 f"{self.settings.AUTH0_URL}/users/{user_id}/roles",
                                 headers={
                                     "Authorization": f"Bearer {token}"
                                 })
        return json.loads(resp.data)
