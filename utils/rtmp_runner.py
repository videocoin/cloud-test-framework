import requests
import logging

logger = logging.getLogger(__name__)


class RTMPRunner:
    def __init__(self, url):
        self.url = url
        self.state = 'NEW'

    def start(self, destination):
        body = {'destination': destination}
        res = requests.post(self.url + '/rtmpjobs/', json=body)
        try:
            res.raise_for_status()
        except requests.HTTPError as e:
            logger.error(
                'Cannot send request to RTMP Runner server. Are you sure '
                'you have the right address / that the server is running?'
            )
            raise e
        self.state = 'RUNNING'

        self.id = res.json()['id']
        return self.id

    def stop(self):
        res = requests.delete(self.url + '/rtmpjobs/' + str(self.id) + '/')
        try:
            res.raise_for_status()
        except requests.HTTPError as e:
            logger.error(
                'Cannot send request to RTMP Runner server. Are you sure '
                'you have the right address / that the server is running?'
            )
            raise e
        self.state = 'COMPLETE'
