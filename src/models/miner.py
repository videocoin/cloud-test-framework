import requests

from src.utils import utils
from src.consts import endpoints


class Miner:
    def __init__(self, cluster, token, id):
        self.cluster = cluster
        self.base_url = utils.get_base_url(self.cluster)
        self.token = token
        self.headers = self._get_headers()
        self.id = id

    def assign_stream(self, stream_id):
        tag = {"tags": [{'key': 'force_task_id', 'value': stream_id}]}
        request = requests.put(
            self.base_url + endpoints.MINER + '/{}'.format(self.id) + '/tags',
            json=tag,
            headers=self.headers,
        )
        request.raise_for_status()

    def _get_headers(self):
        return {'Authorization': 'Bearer ' + self.token}

    def json(self):
        response = requests.get(
            self.base_url + endpoints.MINER + '/' + self.id, headers=self.headers
        )
        response.raise_for_status()

        return response.json()

    @property
    def name(self):
        return self.json()['name']
