import requests

from src.consts import endpoints
from src.models.base import BaseModel


class ProfilesList(BaseModel):
    def all(self):
        response = requests.get(self.base_url + endpoints.PROFILE)
        response.raise_for_status()
        return response.json()['items']


class Profiles(BaseModel):

    def __init__(self, cluster, token, id):
        self.id = id
        super().__init__(cluster, token)

    def json(self):
        response = requests.get(
            self.base_url + endpoints.PROFILE + '/' + self.id, headers=self.headers
        )
        response.raise_for_status()

        return response.json()

    @property
    def name(self):
        return self.json()['name']
