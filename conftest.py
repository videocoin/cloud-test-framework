import math
import os
import re
import logging
import pytest
import requests

from consts import input_values
from consts import endpoints
from models.user import User
from utils.testrail_client import TestRailClient
from utils import utils

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


def pytest_sessionstart(session):
    # TODO: Test run creation should ideally go here
    pass


def pytest_sessionfinish(session):
    # TODO: Test run closing should ideally go here
    pass


def get_output_profile_name(profile):
    return profile['name']


def pytest_generate_tests(metafunc):
    if 'output_profile' in metafunc.fixturenames:
        cluster = metafunc.config.option.cluster
        base_url = utils.get_base_url(cluster)
        try:
            res = requests.get(base_url + endpoints.PROFILE + '1')
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


def pytest_collection_finish(session):
    use_testrail = session.config.getoption('--testrail_report')
    if not use_testrail:
        return

    testrail_email = 'kenneth@liveplanet.net'
    testrail_key = os.getenv('TESTRAIL_KEY')
    if testrail_email is None:
        raise Exception("specify testrail email")
    if testrail_key is None:
        raise Exception("specify testrail key")
    testrail_client = TestRailClient(testrail_email, testrail_key)

    # Create a new empty run, add the test cases to it later
    # run_name = 'VideoCoin cloud testing: ' + datetime.now().strftime(
    #     '%m-%d-%Y@%H:%M:%S %p'
    # )
    run_name = 'fake test run'
    new_run = testrail_client.add_run(12, 473, run_name)
    new_run_id = new_run['id']

    # Sync tests before doing anything
    # BUG: I have an input() call in here. Tests will fail if I try to run this
    # without -s argument in pytest invocation (don't capture stdout)
    is_synced = testrail_client.add_local_tests_to_testrail(session.items)
    if not is_synced:
        raise pytest.UsageError(
            'Not all collected tests are synced with TestRail. '
            'To run tests, sync tests with TestRail or exclude --testrail_report'
            'flag. Aborting.'
        )

    # Get all test cases in TestRail testsuite
    current_existing_testcases = testrail_client.get_all_test_cases(
        project_id=12, test_suite_id=473
    )

    # Get all the display names of the test cases to run and attach TestRail test IDs
    # to the items to be ran
    tests_to_run = []
    for local_testcase in session.items:
        testcase_docstring = local_testcase._obj.__doc__
        name_regex = re.compile(r'Name:\n([\s\S]*)Description:')
        param_name = re.compile(r'\[(.*)\]')
        local_testcase_name = re.search(name_regex, testcase_docstring).group(1).strip()
        if local_testcase.originalname:
            local_testcase_name += ' [{}]'.format(
                re.search(param_name, local_testcase.name).group(1)
            )

        testcase_found = False
        for cloud_testcase in current_existing_testcases:
            if cloud_testcase['title'] == local_testcase_name:
                tests_to_run.append(cloud_testcase['id'])
                local_testcase.user_properties.append(
                    ('testrail_test_id', cloud_testcase['id'])
                )
                local_testcase.user_properties.append(('testrail_run_id', new_run_id))
                testcase_found = True
        if not testcase_found:
            # TODO: Just skip the tests that aren't in TestRail. If there are no more
            # tests to be ran (because none of the tests are in TestRail), _then_ close
            # the test run
            testrail_client.close_test_run(new_run_id)
            raise Exception(
                '"{}" cannot be found. Are you sure local testcases are synced '
                'with TestRail testcases?'.format(local_testcase_name)
            )

    testrail_client.add_tests_to_run(new_run_id, tests_to_run)


def pytest_runtest_makereport(item, call):
    use_testrail = item.session.config.getoption('--testrail_report')
    if not use_testrail:
        return

    testrail_email = 'kenneth@liveplanet.net'
    testrail_key = os.getenv('TESTRAIL_KEY')
    if testrail_email is None:
        raise Exception("specify testrail email")
    if testrail_key is None:
        raise Exception("specify testrail key")
    testrail_client = TestRailClient(testrail_email, testrail_key)

    if call.when == 'call':
        duration = str(math.ceil(call.stop - call.start)) + 's'
        result = {'elapsed': duration}
        # If the item's call has no excinfo (no exception info), then the test passed
        if not call.excinfo:
            result['status_id'] = 1
        else:
            result['status_id'] = 5
        run_id = item.user_properties[1][1]
        case_id = item.user_properties[0][1]
        testrail_client.add_result_for_case(run_id, case_id, result)
