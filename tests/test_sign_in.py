import pytest
import requests

from consts import endpoints
from consts import expected_results
from consts import input_values


def test_sign_in_with_valid_credentials_have_correct_user_information(user):
    # TODO: I wanna do something fancy, but the JSON isn't flat. Maybe I should
    # flatten it before comparing?
    # subset_of_keys_tested = expected_results.TEST_USER_INFORMATION.keys()
    # for key in subset_of_keys_tested:
    #     actual_value = user.json()[key]
    #     expected_value = expected_results.TEST_USER_INFORMATION[key]
    #     assert actual_value == expected_value
    actual_user_values = user.json()
    assert actual_user_values['id'] == expected_results.TEST_USER_INFORMATION['id']
    assert (
        actual_user_values['email'] == expected_results.TEST_USER_INFORMATION['email']
    )
    assert actual_user_values['name'] == expected_results.TEST_USER_INFORMATION['name']
    assert (
        actual_user_values['is_active']
        == expected_results.TEST_USER_INFORMATION['is_active']
    )
    assert (
        actual_user_values['account']['id']
        == expected_results.TEST_USER_INFORMATION['account']['id']
    )
    assert (
        actual_user_values['account']['address']
        == expected_results.TEST_USER_INFORMATION['account']['address']
    )


def test_sign_in_with_non_existant_email_returns_error():
    email = 'really_fake_email@fake.ru'
    password = 'not_a_valid_password'
    with pytest.raises(requests.HTTPError) as e:
        _auth(email, password)

    assert e.value.response.status_code == 401
    assert (
        e.value.response.json()
        == expected_results.SIGN_IN_WITH_NON_EXISTENT_EMAIL_ERROR
    )


def test_sign_in_with_incorrect_password_returns_error():
    email = input_values.ACCOUNT_EMAIL_DEFAULT
    password = 'not_a_valid_password'
    with pytest.raises(requests.HTTPError) as e:
        _auth(email, password)

    assert e.value.response.status_code == 401
    assert (
        e.value.response.json()
        == expected_results.SIGN_IN_WITH_INCORRECT_PASSWORD_ERROR
    )


def _auth(email, password):
    body = {'email': email, 'password': password}

    res = requests.post(endpoints.BASE_URL + endpoints.AUTH, json=body)
    res.raise_for_status()

    return res.json()['token']
