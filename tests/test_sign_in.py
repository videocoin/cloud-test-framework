import pytest
import requests

from consts import endpoints
from consts import expected_results


@pytest.mark.smoke
@pytest.mark.functional
def test_sign_in_with_valid_credentials_have_correct_user_information(user):
    """
    Name:
    Test sign in with valid credentials have correct user information

    Description:
    Users who sign in (and receive a token for front-end authorization and reference)
    should always have the same information when signed in. Most importantly, the user's
    ID and wallet ID (['account']['id']) should stay the same. Other fields of the user
    vary too widely to compare to a single value (VID in wallet, etc.) and is only checked
    that the format of the field is correct.

    Steps:
    0. Sign in with valid credentials to receive JWT token
    0. Use token to retrieve all information about the user

    Expected results:
    0. Server should return correct information about the user
    """
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
        actual_user_values['account']['address']
        == expected_results.TEST_USER_INFORMATION['account']['address']
    )


@pytest.mark.functional
def test_sign_in_with_non_existant_email_returns_error():
    """
    Name:
    Test sign in with non-existent email returns error

    Description:
    Users who attempt to sign in with a non-existent email (valid email address format,
    but the email is not signed up with the service) should receive an error.

    Steps:
    0. Attempt to sign in with an email that is not signed up with the service

    Expected results:
    0. User receives specific error message for non-existent email
    """
    email = 'really_fake_email@fake.ru'
    password = 'not_a_valid_password'
    with pytest.raises(requests.HTTPError) as e:
        _auth(email, password)

    assert e.value.response.status_code == 401
    assert (
        e.value.response.json()
        == expected_results.SIGN_IN_WITH_NON_EXISTENT_EMAIL_ERROR
    )


@pytest.mark.functional
def test_sign_in_with_incorrect_password_returns_error(user):
    """
    Name:
    Test sign in with incorrect password returns error

    Description:
    Users who attempt to sign in with an email that's signed up with the service, but
    enters an incorrect password should receive an error.

    Steps:
    0. Attempt to sign in with an email that is registered, but with an incorrect password

    Expected results:
    0. User receives specific error message for incorrect password
    """
    email = user.email
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
