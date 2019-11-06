import requests
from datetime import datetime

from models.stream import Stream
from consts import endpoints


class StreamManager:
    def __init__(self, token):
        self.token = token
        self.headers = self._get_headers()

    def get_streams(self):
        response = requests.get(
            endpoints.BASE_URL + endpoints.STREAM, headers=self.headers
        )
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

        body = {'name': name, 'profile_id': profile_id}

        response = requests.post(
            endpoints.BASE_URL + endpoints.STREAM, headers=self.headers, json=body
        )
        response.raise_for_status()
        # TODO: Make sure response is good
        return Stream(self.token, response.json()['id'])

    def get_user(self):
        response = requests.get(
            endpoints.BASE_URL + endpoints.USER, headers=self.headers
        ).json()
        response.raise_for_status()
        # TODO: Make sure response is good
        return response.json()

    def _get_profile_ids(self):
        response = requests.get(endpoints.BASE_URL + endpoints.PROFILE)
        response.raise_for_status()
        # TODO: Make sure response is good
        return response.json()['items']

    def _get_headers(self):
        return {'Authorization': 'Bearer ' + self.token}
