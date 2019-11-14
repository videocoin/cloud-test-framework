import re
import logging
import urllib.request
import urllib.error
import json
import base64

logger = logging.getLogger(__name__)


class TestRailClient:
    def __init__(self, email, password):
        TESTRAIL_SERVER = 'https://liveplanet.testrail.io'
        client = APIClient(TESTRAIL_SERVER)
        client.user = email
        client.password = password
        self.client = client

    def get_milestone(self, milestone_id):
        return self.client.send_get('get_milestone/{}'.format(milestone_id))

    def get_run(self, run_id):
        return self.client.send_get('get_run/{}'.format(run_id))

    def get_automated_tests(self, run_id):
        return self.client.send_get('get_tests/{}'.format(run_id))

    def get_all_test_cases(self, project_id, test_suite_id):
        return self.client.send_get(
            'get_cases/{}/&suite_id={}'.format(project_id, test_suite_id)
        )

    def get_all_tests_in_a_run(self, run_id):
        return self.client.send_get('get_tests/{}'.format(run_id))

    def delete_test_case(self, testcase_id):
        return self.client.send_post('delete_case/{}'.format(testcase_id), {})

    def close_test_run(self, run_id):
        return self.client.send_post('close_run/{}'.format(run_id), {})

    def post_results(self, run_id, data):
        return self.client.send_post("add_results/{}".format(run_id), data)

    def add_result_for_case(self, run_id, case_id, data):
        return self.client.send_post(
            'add_result_for_case/{}/{}'.format(run_id, case_id), data
        )

    def delete_run(self, run_id):
        return self.client.send_post('delete_run/{}'.format(run_id))

    def add_run(
        self,
        project_id,
        suite_id,
        # case_ids,
        # assignedto_user_id=0,
        run_name="Sample test run - please change",
    ):

        # Not specifying assignedto_user_id is currently the only way to have the run
        # assigned to "unassigned"
        request_fields = {
            # "assignedto_id": assignedto_user_id,
            "suite_id": suite_id,
            "name": run_name,
            # "case_ids": case_ids,
            # "include_all": False
        }
        return self.client.send_post("add_run/{}".format(project_id), request_fields)

    def add_tests_to_run(self, run_id, case_ids):
        data = {'include_all': False, 'case_ids': case_ids}
        return self.update_run(run_id, data)

    def update_run(self, run_id, data):
        return self.client.send_post('update_run/{}'.format(run_id), data)

    def add_test_case(
        self, name, section_id, description=None, steps=None, expected_results=None
    ):
        request_fields = {
            'title': name,
            'custom_test_description': description,
            'custom_steps': steps,
            'custom_expected': expected_results,
        }
        return self.client.send_post('add_case/' + str(section_id), request_fields)

    def add_local_tests_to_testrail(self, local_testcases):
        TESTRAIL_PROJECT_ID = 12
        TESTRAIL_TEST_SUITE = 473
        TESTRAIL_SECTION = 3427

        current_existing_testcases = self.get_all_test_cases(
            project_id=TESTRAIL_PROJECT_ID, test_suite_id=TESTRAIL_TEST_SUITE
        )

        # We want to programatically add new tests as we write them. Test rail API has
        # a rate limit (180 Requests per minute at the time of writing). If possible,
        # we want to minimize the amount of calls. Let's check what test case are maintained
        # on test rail and add new ones that may be written in this framework
        name_regex = re.compile(r'Name:\n([\s\S]*)Description:')
        param_name = re.compile(r'\[(.*)\]')
        description_regex = re.compile(r'Description:\n([\s\S]*)Steps:')
        steps_regex = re.compile(r'Steps:\n([\s\S]*)Expected results:')
        expected_results_regex = re.compile(r'Expected results:\n([\s\S]*)')
        # add_new_test_cases
        # edit_test_case
        # delete_unused_test_cases (this should be its own util method, should not be run
        # on every test run)
        skip_tests = []
        add_tests = []
        for local_testcase in local_testcases:
            need_to_add_local_test = True
            test_docstring = local_testcase._obj.__doc__

            if test_docstring:
                local_test_name = re.search(name_regex, test_docstring).group(1).strip()
                if local_testcase.originalname:
                    # If a test has an original name, it is a parametrized test and the
                    # parametrized argument should be appended to the name
                    local_test_name = re.search(name_regex, test_docstring).group(
                        1
                    ).strip() + ' [{}]'.format(
                        re.search(param_name, local_testcase.name).group(1)
                    )

                # A test case needs to be added if there is no test case in the TestRail
                # test repository that shares the same name
                for cloud_testcase in current_existing_testcases:
                    cloud_test_display_name = cloud_testcase['title']

                    # It already exists on testrail so break out and check the next
                    # local test cases
                    if cloud_test_display_name == local_test_name:
                        need_to_add_local_test = False
                        skip_tests.append(local_test_name)
                        break

                if need_to_add_local_test:
                    if test_docstring:
                        # TODO: This formatting isn't gonna handle things that aren't in simple
                        # paragraph or simple list form...
                        #
                        # As of right now, description MUST be in a simple paragraph form
                        # Steps and expected results MUST be in numbered list form
                        reformat_paragraph = lambda txt: ' '.join(txt.split())
                        reformat_list = (
                            lambda txt: txt.replace('\n', ' ')
                            .replace('\t', '')
                            .replace('0.', '\n0.')
                        )
                        unformatted_description = (
                            re.search(description_regex, test_docstring)
                            .group(1)
                            .strip()
                        )
                        unformatted_steps = (
                            re.search(steps_regex, test_docstring).group(1).strip()
                        )
                        unformatted_expected_results = (
                            re.search(expected_results_regex, test_docstring)
                            .group(1)
                            .strip()
                        )
                        description = reformat_paragraph(unformatted_description)
                        steps = reformat_list(unformatted_steps)
                        expected_results = reformat_list(unformatted_expected_results)
                        add_tests.append(
                            (
                                local_test_name,
                                TESTRAIL_SECTION,
                                description,
                                steps,
                                expected_results,
                            )
                        )

        if not len(add_tests):
            print('All tests up to date')
            return True
        else:
            print('The following tests are already registered in TestRail: ')
            for test in skip_tests:
                print(test)
            print()

            print('The following tests need to be added into TestRail: ')
            for test in add_tests:
                print('- ' + test[0])

            try:
                confirm = input(
                    'Are you sure you want to add these tests to TestRail? '
                )
                if confirm.lower() == 'y':
                    for test in add_tests:
                        self.add_test_case(*test)
                    return True
                else:
                    return False
            except OSError as e:
                logger.error(
                    'PyTest option -s has to be passed in with --testrail_report'
                    'Enable -s and try again. Aborting tests and test sync'
                )
                raise e


#
# TestRail API binding for Python 3.x (API v2, available since
# TestRail 3.0)
#
# Learn more:
#
# http://docs.gurock.com/testrail-api2/start
# http://docs.gurock.com/testrail-api2/accessing
#
# Copyright Gurock Software GmbH. See license.md for details.
#
class APIClient:
    def __init__(self, base_url):
        self.user = ''
        self.password = ''
        if not base_url.endswith('/'):
            base_url += '/'
        self.__url = base_url + 'index.php?/api/v2/'

    #
    # Send Get
    #
    # Issues a GET request (read) against the API and returns the result
    # (as Python dict).
    #
    # Arguments:
    #
    # uri                 The API method to call including parameters
    #                     (e.g. get_case/1)
    #
    def send_get(self, uri):
        return self.__send_request('GET', uri, None)

    #
    # Send POST
    #
    # Issues a POST request (write) against the API and returns the result
    # (as Python dict).
    #
    # Arguments:
    #
    # uri                 The API method to call including parameters
    #                     (e.g. add_case/1)
    # data                The data to submit as part of the request (as
    #                     Python dict, strings must be UTF-8 encoded)
    #
    def send_post(self, uri, data):
        return self.__send_request('POST', uri, data)

    def __send_request(self, method, uri, data):
        url = self.__url + uri
        request = urllib.request.Request(url)
        if method == 'POST':
            request.data = bytes(json.dumps(data), 'utf-8')

        auth = str(
            base64.b64encode(bytes('%s:%s' % (self.user, self.password), 'utf-8')),
            'ascii',
        ).strip()
        request.add_header('Authorization', 'Basic %s' % auth)
        request.add_header('Content-Type', 'application/json')

        e = None
        try:
            response = urllib.request.urlopen(request).read()
        except urllib.error.HTTPError as ex:
            response = ex.read()
            e = ex

        if response:
            result = json.loads(response.decode())
        else:
            result = {}

        if e is not None:
            if result and 'error' in result:
                error = '"' + result['error'] + '"'
            else:
                error = 'No additional error message received'
            raise APIError('TestRail API returned HTTP %s (%s)' % (e.code, error))

        return result


class APIError(Exception):
    pass
