from time import sleep
import requests
import pdb

from consts import endpoints
from consts import input_values
from utils import utils

def test_password_recovery_with_registered_email():
    email = input_values.VALID_EMAIL
    old_password = input_values.ACCOUNT_PASSWORD_DEFAULT
    new_password = input_values.ACCOUNT_PASSWORD_01

    # Send email to start password recovery
    _start_password_recovery(email)

    # Wait for server to send email
    sleep(5)

    # Get token from recently sent email and change password    
    token = _get_password_reset_token(email)
    _change_password_with_token(token, new_password)

    # Check that the new password works
    _auth(email, new_password)

    # Change password back to old password for future tests
    _start_password_recovery(email)
    sleep(5)
    token = _get_password_reset_token(email)
    _change_password_with_token(token, old_password)

    # Check that changing back to old password works
    _auth(email, old_password)

def _start_password_recovery(email):
    body = {'email': input_values.VALID_EMAIL}
    response = requests.post(endpoints.BASE_URL + endpoints.RECOVERY_START,
        json=body)
    response.raise_for_status()

def _get_password_reset_token(email):
    return utils.get_items_from_email(
        email, input_values.PASSWORD_RECOVERY_SUBJECT,
        input_values.PASSWORD_RECOVERY_REGEX)

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
