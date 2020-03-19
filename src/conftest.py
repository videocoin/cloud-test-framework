import logging
import pytest
import re
from web3 import Web3, HTTPProvider
from web3.middleware import geth_poa_middleware

from src.consts.input_values import (
    get_initial_value, ACCOUNT_EMAIL_DEFAULT, ACCOUNT_PASSWORD_DEFAULT, EMAIL_PASSWORD, SENDGRID_KEY, REPORT_EMAILS
)
from src.models.user import User
from src.models.profiles import ProfilesList
from src.utils import utils
from src.utils.rtmp_runner import RTMPRunner
from src.utils.email import get_report_html, send_report

logger = logging.getLogger(__name__)


def pytest_addoption(parser):
    parser.addoption('--cluster', action='store', default='dev')
    parser.addoption('--num_of_test_users', action='store', default=3)
    parser.addoption('--rtmp_runner', action='store', default='127.0.0.1:8080')
    parser.addoption('--report_emails', action='store', default=False)
    parser.addoption('--sendgrid_key', action='store', default=False)


def pytest_itemcollected(item):
    if item._obj.__doc__:
        parsed_params = re.match(r'^.*[(.+)].*$', item.name)
        if parsed_params:
            parsed_params = parsed_params.group(0)
        else:
            parsed_params = ''
        item._nodeid = '{}[{}]'.format(item._obj.__doc__.strip(), parsed_params)
    else:
        item._nodeid = item.name


def pytest_terminal_summary(terminalreporter, config):
    cluster = config.getoption('--cluster')
    sendgrid_key = get_initial_value(cluster, SENDGRID_KEY)
    report_emails = get_initial_value(cluster, REPORT_EMAILS)
    if not sendgrid_key:
        return
    if not report_emails:
        return

    report_html = get_report_html(
        passed=terminalreporter.stats.get('passed', []),
        failed=terminalreporter.stats.get('failed', []),
        skipped=terminalreporter.stats.get('skipped', []),
        error=terminalreporter.stats.get('error', []),
        cluster=cluster,
    )
    send_report(report_html, sendgrid_key, report_emails)


@pytest.fixture
def cluster(request):
    cluster = request.config.getoption('--cluster')
    return cluster


@pytest.fixture
def user(request):
    cluster = request.config.getoption('--cluster')
    available_clusters = ['snb', 'kili', 'dev']
    if cluster not in available_clusters:
        raise ValueError(
            'Cluster not available. Currently available clusters are {}'.format(
                available_clusters
            )
        )

    email = get_initial_value(cluster, ACCOUNT_EMAIL_DEFAULT)
    password = get_initial_value(cluster, ACCOUNT_PASSWORD_DEFAULT)
    email_password = get_initial_value(cluster, EMAIL_PASSWORD)

    return User(cluster, email, password, email_password)


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
    available_clusters = ['snb', 'dev']
    if cluster not in available_clusters:
        raise ValueError(
            'Cluster not available. Currently available clusters are {}'.format(
                available_clusters
            )
        )
    if cluster in ['snb', 'dev']:
        network_url = 'https://rinkeby.infura.io/v3/2133def9c46e42269dc76cff5338643a'

    w3 = Web3(HTTPProvider(network_url))
    # Still don't really understand this...Read more here:
    # https://web3py.readthedocs.io/en/latest/middleware.html#geth-style-proof-of-authority
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)

    return w3


@pytest.fixture
def abi(request):
    cluster = request.config.getoption('--cluster')
    available_clusters = ['snb', 'dev']
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
        all_profiles = ProfilesList(cluster).all()
        logger.debug('all_profiles {}'.format(all_profiles))
        metafunc.parametrize(
            'output_profile', all_profiles, ids=get_output_profile_name
        )
