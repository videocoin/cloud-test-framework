from time import sleep
import requests
import urllib.parse
import pytest
import logging

from consts import endpoints
from consts import input_values
from consts import email_body_regex
from utils import utils

logger = logging.getLogger(__name__)


def test_password_recovery_with_registered_email():
    email = input_values.ACCOUNT_EMAIL_DEFAULT
    email_password = input_values.EMAIL_PASSWORD
    old_password = input_values.ACCOUNT_PASSWORD_DEFAULT
    new_password = input_values.ACCOUNT_PASSWORD_01

    # Send email to start password recovery
    _start_password_recovery(email)

    # Wait for server to send email
    sleep(3)

    # Get token from recently sent email and change password
    # TODO: This was failing with a 500 server error because the email was
    # never sending and a wrong, invalid token was being used. It'd be nice
    # if I could get an easy reason to find out what's wrong instead of needing
    # to figure out why I'm getting a 500 error (my tests or an actual problem?)
    token = _get_password_reset_token(email, email_password)
    _change_password_with_token(token, new_password)

    # Check that the new password works
    _auth(email, new_password)

    # Change password back to old password for future tests
    _start_password_recovery(email)
    sleep(5)
    token = _get_password_reset_token(email, email_password)
    _change_password_with_token(token, old_password)

    # Check that changing back to old password works
    _auth(email, old_password)


@pytest.mark.parametrize(
    'invalid_email',
    [
        'not_a_registered_email@fake.ru',
        'no_domain_email',
        'invalid#symbol#in#email.gmail.com',
        'consecutive__symbol__email@gmail.com',
        'short_domain_tld@gmail.c',
        'invalid_symbol_in_domain@gmail#com',
        'consecutive_symbol_in_domain@gmail..com',
    ],
)
def test_password_recovery_with_invalid_email_returns_error(invalid_email):
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
