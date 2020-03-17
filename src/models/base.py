from src.utils import utils


class BaseModel:
    endpoint = None

    def __init__(self, cluster, token=None):
        self.cluster = cluster
        self.base_url = utils.get_base_url(self.cluster)

        self.token = token
        if self.token:
            self.headers = self._get_headers()

    def _get_headers(self):
        return {'Authorization': 'Bearer ' + self.token}
