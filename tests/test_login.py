import requests

from consts import endpoints
from consts import expected_results

non_existant_email = 'not_a_real_email@fake.ru'
invalid_password = 'not_a_real_password'

def test_sign_in_with_non_existant_email_gives_error():
    body = {
        'email': non_existant_email,
        'password': invalid_password
    }

    response = requests.post(endpoints.BASE_URL + endpoints.AUTH, json=body)

    assert response.status_code == 401
    assert response.json() == expected_results.SIGN_IN_WITH_NON_EXISTANT_EMAIL_ERROR
