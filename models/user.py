from datetime import datetime
import requests

from models.stream import Stream
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

    def get_streams(self):
        response = requests.get(endpoints.BASE_URL + endpoints.STREAM,
            headers=self.headers)
        response.raise_for_status()
        # TODO: Make sure response is good
        items = response.json()['items']
        stream_objs = []
        for item in items:
            stream_obj = Stream(self.token, item['id'])
            stream_objs.append(stream_obj)
        return stream_objs
        # TODO: This always returns the same ID for all stream objects created
        # return [Stream(self.token, stream['id']) for stream in items]

    def create_stream(self, name=None, profile_name=None, profile_id=None):
        """
        profile_name is only a convenience argument
        profile_id takes precedence over profile_name
        """
        if name == None:
            name = datetime.now().strftime("%m-%d-%Y@%H:%M:%S %p")

        if profile_id == None:
            if profile_name == None:
                profile_name = '720p'
            for profile in self._get_profile_ids():
                if profile['name'] == profile_name:
                    profile_id = profile['id']
            if not profile_id:
                raise ValueError('Profile name does not exist')

        body = {
            'name': name,
            'profile_id': profile_id
        }

        response = requests.post(endpoints.BASE_URL + endpoints.STREAM,
            headers=self.headers, json=body)
        response.raise_for_status()
        # TODO: Make sure response is good
        return Stream(self.token, response.json()['id'])

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

    def _get_profile_ids(self):
        response = requests.get(endpoints.BASE_URL + endpoints.PROFILE)
        response.raise_for_status()
        # TODO: Make sure response is good
        return response.json()['items']
