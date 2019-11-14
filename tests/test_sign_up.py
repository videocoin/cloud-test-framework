import pytest
import requests

from consts import endpoints
from consts import expected_results


@pytest.mark.functional
def test_signing_up_with_an_existing_email_returns_error(user):
    """
    Name:
    Signing up with an existing email returns error

    Description:
    A user that signs up with an email address that has already been registered to the
    service should return an error.

    Steps:
    0. Verify the account attempting to sign up with is already a valid user
    0. Using the same credentials, sign up for the service

    Expected results:
    0. Server should return error describing sign up cannot be complete with email that has already been taken
    """
    email = user.email
    password = user.password
    name = 'Automation Account'

    with pytest.raises(requests.HTTPError) as e:
        _sign_up(email, password, name)

    assert e.value.response.status_code == 400
    assert e.value.response.json() == expected_results.SIGN_UP_WITH_EXISTING_EMAIL_ERROR


@pytest.mark.functional
def test_signing_up_with_short_name_returns_error(user):
    """
    Name:
    Signing up with short name returns error

    Description:
    A user that signs up with a full name that's shorter than 2 characters cannot be
    registered and should return an error.

    Steps:
    0. Sign up for service using a full name shorter than 2 characters

    Expected results:
    0. Server should return error describing sign up cannot be complete with name shorter than 2 characters
    """
    email = user.email
    password = user.password
    name = 'K'

    with pytest.raises(requests.HTTPError) as e:
        _sign_up(email, password, name)

    assert e.value.response.status_code == 400
    assert e.value.response.json() == expected_results.SIGN_UP_WITH_SHORT_NAME_ERROR


@pytest.mark.functional
@pytest.mark.parametrize('password', ['1234567890', 'no_number_password', '2short'])
def test_signing_up_with_invalid_password_returns_error(user, password):
    """
    Name:
    Signing up with invalid password returns error

    Description:
    A user that signs up with a password with an invalid format cannot be registered with
    the service and should be returned an error. Valid passwords must be 8 characters long
    and have a combination of numbers and letters.

    Steps:
    0. Sign up for service using an invalid password format

    Expected results:
    0. Server should return error describing sign up cannot be complete with invalid password format
    """
    email = user.email
    password = password
    name = 'Automation Account'

    with pytest.raises(requests.HTTPError) as e:
        _sign_up(email, password, name)

    assert e.value.response.status_code == 400
    assert e.value.response.json() == expected_results.SIGN_UP_WITH_INVALID_PASSWORD


def _sign_up(email, password, name):
    body = {
        'email': email,
        'password': password,
        'confirm_password': password,
        'name': name,
    }

    res = requests.post(endpoints.BASE_URL + endpoints.SIGN_UP, json=body)
    res.raise_for_status()

    return res.json()
