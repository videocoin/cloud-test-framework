import pytest
import requests

from consts import endpoints
from consts import expected_results


def test_signing_up_with_an_existing_email_returns_error(user):
    email = user.email
    password = user.password
    name = 'Automation Account'

    with pytest.raises(requests.HTTPError) as e:
        _sign_up(email, password, name)

    assert e.value.response.status_code == 400
    assert e.value.response.json() == expected_results.SIGN_UP_WITH_EXISTING_EMAIL_ERROR


def test_signing_up_with_short_name_returns_error(user):
    email = user.email
    password = user.password
    name = 'K'

    with pytest.raises(requests.HTTPError) as e:
        _sign_up(email, password, name)

    assert e.value.response.status_code == 400
    assert e.value.response.json() == expected_results.SIGN_UP_WITH_SHORT_NAME_ERROR


@pytest.mark.parametrize('password', ['1234567890', 'no_number_password', '2short'])
def test_signing_up_with_invalid_password_returns_error(user, password):
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
