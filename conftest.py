import pytest

from consts import input_values
from models.user import User


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
    parser.addoption('--num_of_test_users', action='store', default=3)
    parser.addoption('--rtmp_runner', action='store', default='127.0.0.1:8000')


@pytest.fixture
def user(request):
    email = request.config.getoption('--email')
    password = request.config.getoption('--password')
    email_password = request.config.getoption('--email_password')

    return User(email, password, email_password)


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
