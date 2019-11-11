import requests


class RTMPRunner:
    def __init__(self, url, destination):
        self.url = url
        self.state = 'NEW'
        self.destination = destination

    def start(self):
        body = {'destination': self.destination}
        res = requests.post(self.url + '/rtmpjobs/', json=body)
        res.raise_for_status()
        self.state = 'RUNNING'

        self.id = res.json()['id']
        return self.id

    def stop(self):
        res = requests.delete(self.url + '/rtmpjobs/' + str(self.id) + '/')
        res.raise_for_status()
        self.state = 'COMPLETE'
