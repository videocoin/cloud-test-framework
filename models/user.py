import requests

from models.stream_manager import StreamManager
from consts import endpoints

# This kind of class is reoccurring. It has:
# 1) A token
# 2) Some headers (that currently only wrap the token in an Authorization header)
# 3) Has a JSON representation that you get from the API
# Can I create some kind of super class to wrap these kinds of classes?
class User:
    def __init__(self, token):
        self.token = token
        self.headers = self._get_headers()
        self.json = self._get_json()
        self.id = self._get_json()['id']

    def get_stream_manager(self):
       return StreamManager(self.token)

    # This kind of method is reoccuring. It does:
    # 1) An authenticated request
    # 2) Needs its response verified (make sure it doesn't have 404, 500, etc.)
    # Can I create some kind of decorator for these kinds of methods?
    def _get_json(self):
        response = requests.get(endpoints.BASE_URL + endpoints.USER,
            headers=self.headers)
        response.raise_for_status()
        # TODO: Check that the response is good
        return response.json()

    def _get_headers(self):
        return {'Authorization': 'Bearer ' + self.token}
