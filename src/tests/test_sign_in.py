import pytest
import requests

from src.consts import endpoints
from src.consts import expected_results
from src.utils import utils


@pytest.mark.smoke
@pytest.mark.functional
def test_sign_in_with_valid_credentials_have_correct_user_information(user):
    """
    Check sign in for a correct user account
    """
    # TODO: I wanna do something fancy, but the JSON isn't flat. Maybe I should
    # flatten it before comparing?
    # subset_of_keys_tested = expected_results.TEST_USER_INFORMATION.keys()
    # for key in subset_of_keys_tested:
    #     actual_value = user.json()[key]
    #     expected_value = expected_results.TEST_USER_INFORMATION[key]
    #     assert actual_value == expected_value
    actual_user_values = user.json()
    assert actual_user_values['id'] == expected_results.TEST_USER_INFORMATION[user.cluster]['id']
    assert (
        actual_user_values['email'] == expected_results.TEST_USER_INFORMATION[user.cluster]['email']
    )
    assert actual_user_values['name'] == expected_results.TEST_USER_INFORMATION[user.cluster]['name']
    assert (
        actual_user_values['is_active']
        == expected_results.TEST_USER_INFORMATION[user.cluster]['is_active']
    )
    assert (
        actual_user_values['account']['address']
        == expected_results.TEST_USER_INFORMATION[user.cluster]['account']['address']
    )


@pytest.mark.functional
def test_sign_in_with_non_existant_email_returns_error(user):
    """
    Check sign in for a fake user account
    """
    email = 'really_fake_email@fake.ru'
    password = 'not_a_valid_password'
    with pytest.raises(requests.HTTPError) as e:
        _auth(user.cluster, email, password)

    assert e.value.response.status_code == 401
    assert (
        e.value.response.json()
        == expected_results.SIGN_IN_WITH_NON_EXISTENT_EMAIL_ERROR
    )


@pytest.mark.functional
def test_sign_in_with_incorrect_password_returns_error(user):
    """
    Check sign with wrong password
    """
    email = user.email
    password = 'not_a_valid_password'
    with pytest.raises(requests.HTTPError) as e:
        _auth(user.cluster, email, password)

    assert e.value.response.status_code == 401
    assert (
        e.value.response.json()
        == expected_results.SIGN_IN_WITH_INCORRECT_PASSWORD_ERROR
    )


def _auth(cluster, email, password):
    body = {'email': email, 'password': password}
    base_url = utils.get_base_url(cluster)
    res = requests.post(base_url + endpoints.AUTH, json=body)
    res.raise_for_status()

    return res.json()['token']
