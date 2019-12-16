from time import sleep
import requests
import urllib.parse
import pytest
import logging

from consts import endpoints
from consts import email_body_regex
from utils import utils

logger = logging.getLogger(__name__)


@pytest.mark.smoke
@pytest.mark.functional
@pytest.mark.skip
def test_password_recovery_with_registered_email(user):
    """
    Name:
    Test password recovery with registered email

    Description:
    Initiating and completing the password recovery process of a registered email
    should change the account's password and the user should be able to authenticate
    with the new password.

    Steps:
    0. Initate password recovery process with a registered email address
    0. Wait for user's email to receive password recovery email
    0. Open the latest Password Recovery email and retrieve the password reset token
    0. Use the password reset token with a new password to change the account password
    0. Verify the new password works to log in
    0. Repeat above steps with the old account password to restore account to correct state
    0. Verify the old password works to log in

    Expected results:
    0. User receives Password Recovery email
    0. User is able to use token to create new password
    0. User is able to log in using new password
    0. User's password is reset to old password before test
    """
    email = user.email
    email_password = user.email_password
    old_password = user.password
    new_password = 'brand_n3w_test_p4ssword'

    _start_password_recovery(user.base_url, email)
    sleep(5)
    token = _get_password_reset_token(email, email_password)
    _change_password_with_token(token, new_password)
    _auth(email, new_password)
    _start_password_recovery(user.base_url, email)
    sleep(5)
    token = _get_password_reset_token(email, email_password)
    _change_password_with_token(token, old_password)
    _auth(email, old_password)


@pytest.mark.functional
@pytest.mark.parametrize(
    'invalid_email',
    [
        '',
        'not_a_registered_email@fake.ru',
        'no_domain_email',
        'invalid_symbol_in_domain@gmail#com',
        'consecutive_symbol_in_domain@gmail..com',
    ],
)
def test_password_recovery_with_invalid_email_returns_error(invalid_email):
    """
    Name:
    Test password recovery with invalid email returns error

    Description:
    Starting password recovery process with email that has a variety of errors should
    return an error and should not continue the process.

    Steps:
    0. Initiate process with a variety of invalid emails
    0. Observe response from server

    Expected results:
    0. Server should return with correct error and error object
    """
    with pytest.raises(requests.HTTPError) as e:
        _start_password_recovery(invalid_email)
    assert e.value.response.json() == {
        'message': 'invalid argument',
        'fields': {'email': 'Enter a valid email address'},
    }
    assert e.value.response.status_code == 400


def _start_password_recovery(email):
    body = {'email': email}
    response = requests.post(endpoints.BASE_URL + endpoints.RECOVERY_START, json=body)
    response.raise_for_status()


def _get_password_reset_token(email, email_password):
    subject = 'Password Recovery'
    token_regex = email_body_regex.PASSWORD_RECOVERY_REGEX
    first_url = utils.get_items_from_email(email, email_password, subject, token_regex)
    redirect_url = requests.get(first_url).url
    # redirect_url stores the token in its query param as a URL
    # encoded string. Have to escape the URL encoding before using
    # token in the body of the request
    # token = urllib.parse.unquote(re.search(r'token=(.*)', redirect_url).group(1))
    query_str = getattr(urllib.parse.urlparse(redirect_url), 'query')
    token = urllib.parse.parse_qsl(query_str)[0][1]

    logger.debug('first_url: %s', first_url)
    logger.debug('redirect_url: %s', redirect_url)
    logger.debug('token: %s', token)

    return token


def _change_password_with_token(token, new_password):
    body = {'token': token, 'password': new_password, 'confirm_password': new_password}
    response = requests.post(endpoints.BASE_URL + endpoints.RECOVER, json=body)
    response.raise_for_status()


def _auth(email, password):
    body = {'email': email, 'password': password}
    response = requests.post(endpoints.BASE_URL + endpoints.AUTH, json=body)
    response.raise_for_status()
