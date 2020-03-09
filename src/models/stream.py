from time import sleep
from datetime import datetime
import logging

import requests
from src.consts import endpoints
from src.utils import utils

logger = logging.getLogger(__name__)

BAD_STATUSES = ['STREAM_STATUS_CANCELLED', 'STREAM_STATUS_FAILED']


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

        return response.json()

    def wait_for_status(self, status, timeout=120):
        start = datetime.now()
        while self.status != status and utils.time_from_start(start) <= timeout:
            if self.status in BAD_STATUSES:
                logger.debug(
                    'Time: {} | Bad stream status: {}'.format(
                        utils.time_from_start(start), self.status
                    )
                )
                break
            logger.debug(
                'Time: {} | Current status: {} | Waiting for status: {}'.format(
                    utils.time_from_start(start), self.status, status
                )
            )
            sleep(1)
        if utils.time_from_start(start) > timeout:
            raise RuntimeError(
                'Stream {} took too long to transition to {}. '
                'Time allowed: {}. Status during failure: {}'.format(
                    self.id, status, timeout, self.status
                )
            )
        return utils.time_from_start(start)

    def is_hls_playlist_healthy(self, duration, expected_update_duration=10):
        start = datetime.now()
        base_playlist_url = 'https://streams-{}.videocoin.network/{}/index.m3u8'
        durations = []

        playlist_url = base_playlist_url.format(self.cluster, self.id)

        last = ''
        last_time = None

        while utils.time_from_start(start) < duration:
            res = requests.get(playlist_url)
            if last != res.text:
                if last_time is not None:
                    try:
                        last_chunk = res.text.split('\n')[-2]
                        logger.debug('last chunk: {}'.format(last_chunk))
                    except IndexError:
                        continue
                    logger.debug('took {} to update'.format(datetime.now() - last_time))
                    durations.append((datetime.now() - last_time).total_seconds())
                    if utils.time_from_start(last_time) > expected_update_duration:
                        raise RuntimeError(
                            'Transcoder took too long to create new chunk. '
                            'Expected duration: {} | Actual duration: {}'.format(
                                expected_update_duration,
                                utils.time_from_start(last_time),
                            )
                        )
                last = res.text
                last_time = datetime.now()
            sleep(0.5)

        logger.debug(
            'Average time to update {}'.format(sum(durations) / len(durations))
        )
        return True

    def check_playlist(self):
        base_playlist_url = 'https://streams-{}.videocoin.network/{}/index.m3u8'
        playlist_url = base_playlist_url.format(self.cluster, self.id)

        res = requests.get(playlist_url)
        last_chunk = res.text.split('\n')[-2]
        logger.debug('last chunk: {}'.format(last_chunk))
        return last_chunk

    def wait_for_playlist_size(self, expected_num_chunks, timeout_per_chunk=20):
        start_time = datetime.now()
        playlist_url = 'https://streams-snb.videocoin.network/{}/index.m3u8'.format(
            self.id
        )
        current_num_chunks = 0
        last_chunk = 0
        last_chunk_update = datetime.now()

        while (
            current_num_chunks < expected_num_chunks
            and (datetime.now() - last_chunk_update).total_seconds() < timeout_per_chunk
        ):
            res = requests.get(playlist_url)
            lines = res.text.split('\n')
            chunks = [lines[i + 1] for i in range(len(lines)) if '#EXTINF' in lines[i]]
            current_num_chunks = len(chunks)
            logger.debug(
                'Current number of chunks in stream {}: {}'.format(
                    self.id, current_num_chunks
                )
            )
            if current_num_chunks > last_chunk:
                last_chunk = current_num_chunks
                last_chunk_update = datetime.now()
            sleep(1)

        if (datetime.now() - last_chunk_update).total_seconds() > timeout_per_chunk:
            raise RuntimeError(
                'Transcoder took too long to create new chunk. '
                'Expected duration: {}'.format(timeout_per_chunk)
            )

        end_time = datetime.now()
        logger.debug(
            'Time it took to wait for {} chunks: {}'.format(
                expected_num_chunks, end_time - start_time
            )
        )

        return end_time - start_time

    def upload_file(self, path):
        with open(path, 'rb') as f:
            response = requests.post(
                self.base_url + endpoints.FILE_UPLOAD + self.id, files={'file': f}, headers=self.headers
            )
        response.raise_for_status()

        return True

    def upload_url(self, file_url):
        response = requests.post(
            self.base_url + endpoints.URL_UPLOAD + self.id, json={'url': file_url}, headers=self.headers
        )
        response.raise_for_status()

        return True

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
