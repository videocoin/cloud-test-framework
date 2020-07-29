import pytest
import requests

from src.consts import endpoints
from src.consts.input_values import TEST_USER_INFORMATION
from src.consts import expected_results
from src.utils import utils
from src.utils.mixins import VideocoinMixin


class TestSignIn(VideocoinMixin):

    @pytest.mark.smoke
    @pytest.mark.functional
    def test_sign_in_with_valid_credentials_have_correct_user_information(self, user):
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
        print(actual_user_values)
        expected_results = self.get_initial_value(TEST_USER_INFORMATION)
        assert actual_user_values['id'] == expected_results['id']
        assert (
            actual_user_values['email'] == expected_results['email']
        )
        assert actual_user_values['first_name'] == expected_results['first_name']
        assert actual_user_values['last_name'] == expected_results['last_name']
        assert (
            actual_user_values['is_active']
            == expected_results['is_active']
        )

    @pytest.mark.functional
    def test_sign_in_with_non_existant_email_returns_error(self, user):
        """
        Check sign in for a fake user account
        """
        email = 'really_fake_email@fake.ru'
        password = 'not_a_valid_password'
        with pytest.raises(requests.HTTPError) as e:
            self.auth(user.cluster, email, password)
    
        assert e.value.response.status_code == 401
        assert (
            e.value.response.json()
            == expected_results.SIGN_IN_WITH_NON_EXISTENT_EMAIL_ERROR
        )
    
    @pytest.mark.functional
    def test_sign_in_with_incorrect_password_returns_error(self, user):
        """
        Check sign with wrong password
        """
        email = user.email
        password = 'not_a_valid_password'
        with pytest.raises(requests.HTTPError) as e:
            self.auth(user.cluster, email, password)
    
        assert e.value.response.status_code == 401
        assert (
            e.value.response.json()
            == expected_results.SIGN_IN_WITH_INCORRECT_PASSWORD_ERROR
        )
    
    def auth(self, cluster, email, password):
        body = {'email': email, 'password': password}
        base_url = utils.get_base_url(cluster)
        res = requests.post(base_url + endpoints.AUTH, json=body)
        res.raise_for_status()
    
        return res.json()['token']
