from datetime import datetime
import logging
import requests

from models.stream import Stream
from consts import endpoints

# This kind of class is reoccurring. It has:
# 1) A token
# 2) Some headers (that currently only wrap the token in an Authorization header)
# 3) Has a JSON representation that you get from the API
# Can I create some kind of super class to wrap these kinds of classes?

logger = logging.getLogger(__name__)


class User:
    def __init__(self, token):
        self.token = token
        self.headers = self._get_headers()
        self.id = self.json()['id']

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

        output_profiles = self._get_output_profiles()
        if profile_id == None:
            if profile_name == None:
                # If profile_id nor profile_name is specified, assume
                # user will take any profile (the first)
                profile_id = output_profiles[0]['id']
            else:
                for profile in output_profiles:
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

    def start_withdraw(self, address, amount):
        body = {'address': address, 'amount': amount}
        logger.debug('address: %s', address)
        logger.debug('amount: %d', amount)

        res = requests.post(
            endpoints.BASE_URL + endpoints.START_WITHDRAW,
            headers=self.headers,
            json=body,
        )
        res.raise_for_status()

        return res.json()['transfer_id']

    def confirm_withdraw(self, transfer_id, pin):
        url = endpoints.BASE_URL + endpoints.CONFIRM_WITHDRAW
        body = {'transfer_id': transfer_id, 'pin': pin}
        logger.debug('transfer_id: %s', transfer_id)
        logger.debug('pin: %s', pin)

        res = requests.post(url, headers=self.headers, json=body)
        logger.debug('response from {}: {}'.format(url, res.json()))
        res.raise_for_status()

        return res.json()

    # This kind of method is reoccuring. It does:
    # 1) An authenticated request
    # 2) Needs its response verified (make sure it doesn't have 404, 500, etc.)
    # Can I create some kind of decorator for these kinds of methods?
    # Maybe all 'test_objects' (like User and Stream) should implement a json()...
    def json(self):
        response = requests.get(
            endpoints.BASE_URL + endpoints.USER, headers=self.headers
        )
        response.raise_for_status()

        return response.json()

    @property
    def email(self):
        return self.json()['email']

    @property
    def name(self):
        return self.json()['name']

    @property
    def is_active(self):
        return self.json()['is_active']

    @property
    def wallet_id(self):
        return self.json()['account']['id']

    @property
    def wallet_address(self):
        return self.json()['account']['address']

    @property
    def wallet_balance(self):
        return self.json()['account']['balance']

    @property
    def wallet_update_at(self):
        return self.json()['account']['update_at']

    def _get_headers(self):
        return {'Authorization': 'Bearer ' + self.token}

    def _get_output_profiles(self):
        response = requests.get(endpoints.BASE_URL + endpoints.PROFILE)
        response.raise_for_status()

        return response.json()['items']
