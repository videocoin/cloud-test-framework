from time import sleep
import re
import requests
import pytest

from consts import endpoints
from consts import expected_results
from consts import input_values
from utils import utils

def test_password_recovery_with_registered_email():
    email = input_values.ACCOUNT_EMAIL_DEFAULT
    email_password = input_values.EMAIL_PASSWORD
    old_password = input_values.ACCOUNT_PASSWORD_DEFAULT
    new_password = input_values.ACCOUNT_PASSWORD_01

    # Send email to start password recovery
    _start_password_recovery(email)

    # Wait for server to send email
    sleep(5)

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

@pytest.mark.xfail(reason=
    """
    I'm pretty sure this should return something with a more descriptive message
    Check expected_results.py to see what the current message is
    """)
def test_password_recovery_with_nonexistent_email_returns_error():
    email = input_values.NONEXISTANT_EMAIL
    with pytest.raises(requests.HTTPError) as e:
        _start_password_recovery(email)
    assert e.value.response.json() == expected_results.PASSWORD_RECOVERY_WITH_NONEXISTENT_EMAIL_ERROR
    assert e.value.response.status_code == 400

# TODO: I should probably be parametrizing this test with the one above
# and all other invalid email tests
def test_password_recovery_with_invalid_email_returns_error():
    email = input_values.INVALID_EMAIL_NO_AT_SIGN
    with pytest.raises(requests.HTTPError) as e:
        _start_password_recovery(email)
    assert e.value.response.json() == expected_results.PASSWORD_RECOVERY_WITH_INVALID_EMAIL_ERROR
    assert e.value.response.status_code == 400

def _start_password_recovery(email):
    body = {'email': email}
    response = requests.post(endpoints.BASE_URL + endpoints.RECOVERY_START,
        json=body)
    response.raise_for_status()

def _get_password_reset_token(email, email_password):
    first_url = utils.get_items_from_email(
        email, email_password,
        input_values.PASSWORD_RECOVERY_SUBJECT,
        input_values.PASSWORD_RECOVERY_REGEX)
    redirect_url = requests.get(first_url).url
    result = re.search(r'token=(.*)', redirect_url).group(1)

    return result

def _change_password_with_token(token, new_password):
    body = {
        'token': token,
        'password': new_password,
        'confirm_password': new_password}
    response = requests.post(endpoints.BASE_URL + endpoints.RECOVER,
        json=body)
    response.raise_for_status()

def _auth(email, password):    
    body = {
        'email': email,
        'password': password}
    response = requests.post(endpoints.BASE_URL + endpoints.AUTH,
        json=body)
    response.raise_for_status()
