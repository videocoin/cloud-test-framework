import logging
import pytest
import requests
from web3 import Web3, HTTPProvider
from web3.middleware import geth_poa_middleware

from consts import input_values
from consts import endpoints
from models.user import User
from utils import utils
from utils.rtmp_runner import RTMPRunner

logger = logging.getLogger(__name__)


def pytest_addoption(parser):
    parser.addoption(
        '--email', action='store', default=input_values.ACCOUNT_EMAIL_DEFAULT
    )
    parser.addoption(
        '--email_password', action='store', default=input_values.EMAIL_PASSWORD
    )
    parser.addoption(
        '--password', action='store', default=input_values.ACCOUNT_PASSWORD_DEFAULT
    )
    parser.addoption('--token', action='store', default=None)
    parser.addoption('--cluster', action='store', default='snb')
    parser.addoption('--num_of_test_users', action='store', default=3)
    parser.addoption('--rtmp_runner', action='store', default='192.168.1.159:8000')
    parser.addoption('--testrail_report', action='store', default=False)


@pytest.fixture
def user(request):
    cluster = request.config.getoption('--cluster')
    available_clusters = ['snb', 'prod']
    if cluster not in available_clusters:
        raise ValueError(
            'Cluster not available. Currently available clusters are {}'.format(
                available_clusters
            )
        )
    email = request.config.getoption('--email')
    password = request.config.getoption('--password')
    email_password = request.config.getoption('--email_password')
    token = request.config.getoption('--token')

    return User(cluster, email, password, email_password, token)


@pytest.fixture
def users(request):
    num_of_test_users = request.config.getoption('--num_of_test_users')
    test_user_base_email = 'vcautomation'
    test_user_domain = 'gmail.com'
    test_user_email_password = 'VideoCoin16!'
    test_user_password = 'tester123'

    list_of_users = []
    for i in range(num_of_test_users):
        num = '0' + str(i) if i < 10 else i
        email = test_user_base_email + num + '@' + test_user_domain
        list_of_users.append(User(email, test_user_password, test_user_email_password))

    return list_of_users


@pytest.fixture
def rtmp_runner(request):
    addr = request.config.getoption('--rtmp_runner')
    return RTMPRunner(addr)


@pytest.fixture
def w3(request):
    cluster = request.config.getoption('--cluster')
    available_clusters = ['snb']
    if cluster not in available_clusters:
        raise ValueError(
            'Cluster not available. Currently available clusters are {}'.format(
                available_clusters
            )
        )
    if cluster == 'snb':
        network_url = 'https://rinkeby.infura.io'

    w3 = Web3(HTTPProvider(network_url))
    # Still don't really understand this...Read more here:
    # https://web3py.readthedocs.io/en/latest/middleware.html#geth-style-proof-of-authority
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)

    return w3


@pytest.fixture
def abi(request):
    cluster = request.config.getoption('--cluster')
    available_clusters = ['snb']
    if cluster not in available_clusters:
        raise ValueError(
            'Cluster not available. Currently available clusters are {}'.format(
                available_clusters
            )
        )
    return utils.get_vid_erc20_abi(cluster)


def get_output_profile_name(profile):
    return profile['name']


def pytest_generate_tests(metafunc):
    # Used to dynamically get all output profiles available for tests that parametrize
    # profiles for tests
    if 'output_profile' in metafunc.fixturenames:
        cluster = metafunc.config.option.cluster
        base_url = utils.get_base_url(cluster)
        try:
            res = requests.get(base_url + endpoints.PROFILE)
            all_profiles = res.json()['items']
            metafunc.parametrize(
                'output_profile', all_profiles, ids=get_output_profile_name
            )
        except KeyError:
            logger.warning(
                '\nGetting output profiles failed. Ignore results for {} | '
                'Current response of /profiles: {}'.format(metafunc.function, res)
            )
            all_profiles = []
            metafunc.parametrize('output_profile', all_profiles)
