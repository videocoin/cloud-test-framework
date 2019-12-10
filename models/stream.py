import requests
from consts import endpoints
from utils import utils


class Stream:
    def __init__(self, cluster, token, id):
        self.cluster = cluster
        self.base_url = utils.get_base_url(self.cluster)
        self.token = token
        self.headers = self._get_headers()
        self.id = id

    def start(self):
        response = requests.post(
            self.base_url + endpoints.STREAM + '/' + self.id + '/run',
            headers=self.headers,
        )
        response.raise_for_status()

        return response.json()

    def stop(self):
        response = requests.post(
            self.base_url + endpoints.STREAM + '/' + self.id + '/stop',
            headers=self.headers,
        )
        response.raise_for_status()

        return response.json()

    def delete(self):
        response = requests.delete(
            self.base_url + endpoints.STREAM + '/' + self.id, headers=self.headers
        )
        response.raise_for_status()

        return True

    def _get_headers(self):
        return {'Authorization': 'Bearer ' + self.token}

    def json(self):
        response = requests.get(
            self.base_url + endpoints.STREAM + '/' + self.id, headers=self.headers
        )
        response.raise_for_status()
        # TODO: Make sure response was good here
        return response.json()

    @property
    def name(self):
        return self.json()['name']

    @property
    def input_url(self):
        return self.json()['input_url']

    @property
    def output_url(self):
        return self.json()['output_url']

    @property
    def stream_contract_id(self):
        return self.json()['stream_contract_id']

    @property
    def stream_contract_address(self):
        return self.json()['stream_contract_address']

    @property
    def status(self):
        return self.json()['status']

    @property
    def input_status(self):
        return self.json()['input_status']

    @property
    def created_at(self):
        # TODO: Do I wanna wrap this in a datetime instance?
        return self.json()['created_at']

    @property
    def updated_at(self):
        return self.json()['updated_at']

    @property
    def ready_at(self):
        return self.json()['ready_at']

    @property
    def completed_at(self):
        return self.json()['completed_at']

    @property
    def rtmp_url(self):
        return self.json()['rtmp_url']
