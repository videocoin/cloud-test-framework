import requests

from consts import endpoints
from consts import expected_results
from consts import input_values


def test_sign_in_with_non_existant_email_gives_error():
    body = {
        'email': input_values.NON_EXISTANT_EMAIL,
        'password': input_values.INVALID_PASSWORD
    }

    response = requests.post(endpoints.BASE_URL + endpoints.AUTH, json=body)

    assert response.status_code == 401
    assert response.json() == expected_results.SIGN_IN_WITH_NON_EXISTANT_EMAIL_ERROR
