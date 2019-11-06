import pytest
import requests

from models.user import User
from consts import endpoints


def pytest_addoption(parser):
    parser.addoption('--email', action='store', default='kgoautomation@gmail.com')
    parser.addoption('--password', action='store', default='tester123')


@pytest.fixture
def user(request):
    email = request.config.getoption('--email')
    password = request.config.getoption('--password')

    body = {'email': email, 'password': password}

    response = requests.post(endpoints.BASE_URL + endpoints.AUTH, json=body)
    # TODO: Make sure response is good
    token = response.json()['token']

    return User(token)
