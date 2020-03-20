import logging
import requests

from src.consts import endpoints
from src.utils import utils

# This kind of class is reoccurring. It has:
# 1) A token
# 2) Some headers (that currently only wrap the token in an Authorization header)
# 3) Has a JSON representation that you get from the API
# Can I create some kind of super class to wrap these kinds of classes?

logger = logging.getLogger(__name__)


class User:
    def __init__(self, cluster, email, password, email_password):
        self.cluster = cluster
        self.base_url = utils.get_base_url(self.cluster)
        self.token = self._get_token(email, password)
        self.headers = self._get_headers()

        self.password = password
        self.email_password = email_password

    def start_withdraw(self, address, amount):
        body = {'address': address, 'amount': str(amount)}
        logger.debug('address: {}'.format(address))
        logger.debug('amount in wei: {}'.format(amount))

        res = requests.post(
            self.base_url + endpoints.START_WITHDRAW, headers=self.headers, json=body
        )
        res.raise_for_status()

        return res.json()['transfer_id']

    def confirm_withdraw(self, transfer_id, pin):
        url = self.base_url + endpoints.CONFIRM_WITHDRAW
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
        response = requests.get(self.base_url + endpoints.USER, headers=self.headers)
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
        return int(self.json()['account']['balance'])

    @property
    def wallet_update_at(self):
        return self.json()['account']['update_at']

    def _get_headers(self):
        return {'Authorization': 'Bearer ' + self.token}

    def _get_token(self, email, password):
        body = {'email': email, 'password': password}

        response = requests.post(self.base_url + endpoints.AUTH, json=body)
        response.raise_for_status()

        return response.json()['token']
