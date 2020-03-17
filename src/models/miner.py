import requests

from src.consts import endpoints
from src.models.base import BaseModel


class MinerList(BaseModel):
    def all(self):
        response = requests.get(self.base_url + endpoints.MINER + '/all')
        response.raise_for_status()
        return response.json()

    def my(self):
        response = requests.get(
            self.base_url + endpoints.MINER, headers=self.headers
        )
        response.raise_for_status()

        return response.json()


class Miner(BaseModel):

    def __init__(self, cluster, token, id):
        self.id = id
        super().__init__(cluster, token)

    def json(self):
        response = requests.get(
            self.base_url + endpoints.MINER + '/' + self.id, headers=self.headers
        )
        response.raise_for_status()

        return response.json()

    @property
    def name(self):
        return self.json()['name']
