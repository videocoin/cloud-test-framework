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


@pytest.fixture
def user(request):
    email = request.config.getoption('--email')
    password = request.config.getoption('--password')
    email_password = request.config.getoption('--email_password')

    return User(email, password, email_password)
